# app.py
import os
import json
import sqlite3
import traceback
from typing import List, Dict, Any

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from rapidfuzz import fuzz
import requests

# load env first
load_dotenv(override=True)


# Create Groq client after loading env (delayed import to avoid crashes if key missing)
from groq import Groq

GROQ_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_KEY:
    print("WARNING: GROQ_API_KEY not found in environment. AI fallback will fail until set.")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None



DB_PATH = os.getenv("DB_PATH", "recipes.db")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

app = Flask(__name__)
CORS(app)


# ---------- DB loaders ----------
def load_recipes() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, type, ingredients, steps, metadata FROM recipes")
    rows = c.fetchall()
    recipes = []
    for r in rows:
        id_, name, typ, ingredients_json, steps_json, metadata_json = r
        try:
            ingredients = json.loads(ingredients_json)
        except Exception:
            ingredients = []
        try:
            steps = json.loads(steps_json)
        except Exception:
            steps = []
        try:
            metadata = json.loads(metadata_json) if metadata_json else {}
        except Exception:
            metadata = {}
        recipes.append({
            "id": id_,
            "name": name,
            "type": typ,
            "ingredients": ingredients,
            "steps": steps,
            "metadata": metadata
        })
    conn.close()
    return recipes


def load_substitutions() -> Dict[str, List[str]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ingredient, substitutes FROM substitutions")
    rows = c.fetchall()
    subs = {}
    for ing, sub_json in rows:
        try:
            subs[ing] = json.loads(sub_json)
        except Exception:
            subs[ing] = []
    conn.close()
    return subs


RECIPES = load_recipes()
SUBSTITUTIONS = load_substitutions()


# ---------- helpers ----------
def normalize_list(items: List[str]) -> List[str]:
    return [str(s).strip().lower() for s in items if s]


def score_recipe_match(user_ingredients: List[str], desired_type: str):
    ui = set(normalize_list(user_ingredients))
    scored = []
    for r in RECIPES:
        r_ings = set(normalize_list(r.get("ingredients", [])))
        overlap = len(ui & r_ings)
        ratio = overlap / max(1, len(r_ings))
        type_score = 20 if desired_type and desired_type.lower() in (r.get("type") or "").lower() else 0
        final_score = type_score + int(ratio * 80)
        scored.append((final_score, ratio, overlap, r))
    scored.sort(reverse=True, key=lambda x: (x[0], x[1], x[2]))
    return scored


def find_substitute(ingredient: str, allergies: List[str]) -> List[str]:
    ing = ingredient.lower()
    # direct mapping
    if ing in SUBSTITUTIONS:
        return [s for s in SUBSTITUTIONS[ing] if s.lower() not in normalize_list(allergies)]
    # fuzzy match
    for key in SUBSTITUTIONS.keys():
        if fuzz.ratio(ing, key) > 85:
            return [s for s in SUBSTITUTIONS[key] if s.lower() not in normalize_list(allergies)]
    return []


def avoid_allergens_in_steps(steps: List[Dict[str, str]], allergies: List[str]):
    allergies_norm = normalize_list(allergies)
    adapted = []
    for step in steps:
        text = step.get("text", "")
        note = ""
        lower = text.lower()
        for a in allergies_norm:
            if a in lower:
                note = f"(NOTE: Step mentions '{a}', which is in your allergies — use substitute or skip.)"
                break
        adapted.append({"text": text, "note": note})
    return adapted


# ---------- AI fallback / parsing ----------
def generate_recipe_with_groq(ingredients, desired_type, allergies):

    prompt = f"""
You are a professional chef.

Generate a REAL recipe for the dish: {desired_type}.

Compare the user's available ingredients: {ingredients}
Allergies: {allergies}

Your tasks:
1. List full correct ingredients for the dish.
2. Identify which of these ingredients the user does NOT have.
3. Suggest substitutes for missing ingredients (avoid allergens).
4. Write clear step-by-step instructions.
5. Provide the most relevant YouTube recipe link based on the dish.

Return STRICT JSON ONLY:

{{
  "name": "",
  "type": "{desired_type}",
  "ingredients_required": [],
  "missing_ingredients": [],
  "substitutes": {{
      "ingredient": ["sub1", "sub2"]
  }},
  "steps": [
      {{"text": ""}}
  ]}}
"""

    if not client:
        return {"ai_generated": True, "error": "AI client not configured (missing GROQ_API_KEY)"}

    raw = ""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=700
        )

        raw = response.choices[0].message.content.strip()

        # Extract JSON
        json_start = raw.find("{")
        json_end = raw.rfind("}") + 1
        json_text = raw[json_start:json_end]

        recipe = json.loads(json_text)
        return {"ai_generated": True, "recipe": recipe}

    except Exception as e:
        print("AI parse error:", e)
        return {
            "ai_generated": True,
            "recipe": {
                "name": "AI Recipe (Unparsed)",
                "type": desired_type,
                "ingredients_required": ingredients,
                "missing_ingredients": [],
                "substitutes": {},
                "steps": [{"text": raw}],
                "suggested_video": None
            }
        }




def process_ai_recipe(ai_recipe: Dict[str, Any], user_ingredients: List[str], allergies: List[str]) -> Dict[str, Any]:
    """
    Normalize and enrich the AI recipe:
    - ensure proper lists
    - compute missing ingredients
    - compute substitutes per missing ingredient (avoid allergens)
    - adapt steps for allergies
    - flag allergens in ingredients_required AND show substitute suggestions
    """
    # ---------- basic validation ----------
    if not isinstance(ai_recipe, dict):
        return {"error": "AI returned invalid recipe format"}

    # ---------- basic fields ----------
    name = ai_recipe.get("name") or ai_recipe.get("title") or "AI Recipe"
    rtype = ai_recipe.get("type") or ""

    # ingredients list (tolerant)
    ingredients_required = ai_recipe.get("ingredients_required") or ai_recipe.get("ingredients") or []
    if isinstance(ingredients_required, str):
        ingredients_required = [x.strip() for x in ingredients_required.split(",") if x.strip()]
    elif not isinstance(ingredients_required, list):
        ingredients_required = [str(ingredients_required)]

    # ---------- normalize steps ----------
    steps_raw = ai_recipe.get("steps") or []
    normalized_steps: List[Dict[str, str]] = []

    if isinstance(steps_raw, list):
        for s in steps_raw:
            if isinstance(s, dict):
                txt = (s.get("text") or "").strip()
                if txt:
                    normalized_steps.append({"text": txt})
            elif isinstance(s, str):
                txt = s.strip()
                if txt:
                    normalized_steps.append({"text": txt})
    elif isinstance(steps_raw, str):
        for ln in [l.strip() for l in steps_raw.splitlines() if l.strip()]:
            normalized_steps.append({"text": ln})

    # ---------- ingredients + allergy + substitutes ----------
    user_set = set(normalize_list(user_ingredients))
    allergies_norm = normalize_list(allergies)

    def is_allergen(ing: str) -> bool:
        ing_l = ing.lower()
        return any(a in ing_l or ing_l in a for a in allergies_norm)

    # raw list we use for logic
    raw_req = [str(x).strip() for x in ingredients_required if str(x).strip()]

    display_ingredients: List[str] = []
    allergen_ingredients: List[str] = []

    for ing in raw_req:
        if is_allergen(ing):
            allergen_ingredients.append(ing)

            # substitutes for this allergen
            subs_for_allergen = find_substitute(ing, allergies)
            if subs_for_allergen:
                subs_preview = ", ".join(str(s) for s in subs_for_allergen[:2])  # first 2
                display_ingredients.append(f"{ing} (⚠ ALLERGEN — try: {subs_preview})")
            else:
                display_ingredients.append(f"{ing} (⚠ ALLERGEN)")
        else:
            display_ingredients.append(ing)

    # ---------- missing ingredients ----------
    missing = [ing for ing in raw_req if ing.lower() not in user_set]

    # ---------- substitutes for missing ingredients ----------
    subs_map: Dict[str, List[str]] = {}
    for miss in missing:
        subs = find_substitute(miss, allergies)
        if subs:
            subs_map[miss] = subs

    # ---------- suggested video (can be None; frontend doesn’t break) ----------

    # ---------- adapt steps for allergies ----------
    adapted_steps = avoid_allergens_in_steps(normalized_steps, allergies)

    return {
        "name": name,
        "type": rtype,
        "ingredients_required": display_ingredients,   # this is what your frontend shows
        "missing_ingredients": missing,
        "substitutes": subs_map,
        "steps": adapted_steps,
        "allergen_ingredients": allergen_ingredients
    }





# ---------- MAIN API ----------
@app.route("/api/recipe", methods=["POST"])
def get_recipe():
    body = request.get_json() or {}
    user_ingredients = body.get("ingredients", [])
    desired_type = body.get("desired_type", "") or body.get("dish", "")
    allergies = body.get("allergies", []) or []
    allow_subs = body.get("allow_substitutions", True)
    use_youtube = body.get("use_youtube", True)

    # Score DB recipes
    scored = score_recipe_match(user_ingredients, desired_type)
    candidates = []
    for score, ratio, overlap, r in scored:
        if ratio >= 0.6:
            candidates.append(r)

    # If DB has matches -> return DB results
    if candidates:
        results = []
        for r in candidates:
            missing, subs = [], {}
            try:
                missing, subs = (lambda ri, ui: (
                    [ing for ing in ri if ing.lower() not in set(normalize_list(ui))],
                    {ing: find_substitute(ing, allergies) for ing in ri if ing.lower() not in set(normalize_list(ui)) and find_substitute(ing, allergies)}
                ))(r["ingredients"], user_ingredients)
            except Exception:
                missing, subs = [], {}
            adapted_steps = avoid_allergens_in_steps(r.get("steps", []), allergies)
            results.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "type": r.get("type"),
                "required_ingredients": r.get("ingredients"),
                "missing_ingredients": missing,
                "substitutes": subs if allow_subs else {},
                "steps": adapted_steps,
                "metadata": r.get("metadata", {})
            })
        return jsonify({"ai_generated": False, "candidates": results})

    # No DB match -> call AI fallback
    ai_result = generate_recipe_with_groq(user_ingredients, desired_type, allergies)
    # If Groq failed outright:
    if ai_result.get("error") or ai_result.get("recipe") is None:
        return jsonify({"ai_generated": True, "error": ai_result.get("error", "AI generation failed")}), 500

    processed = process_ai_recipe(ai_result["recipe"], user_ingredients, allergies)

    # If allow_subs == False, strip substitutes
    if not allow_subs and "substitutes" in processed:
        processed["substitutes"] = {}

    return jsonify({"ai_generated": True, "recipe": processed})


@app.route("/api/recipes/list", methods=["GET"])
def list_recipes():
    return jsonify([{"id": r["id"], "name": r["name"], "type": r["type"]} for r in RECIPES])

from flask import render_template

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
