# create_sample_db.py
import sqlite3
import json

DB = "recipes.db"

recipes = [
    {
        "id": 1,
        "name": "Simple Tomato Pasta",
        "type": "pasta",
        "ingredients": ["pasta", "tomato", "onion", "garlic", "olive oil", "salt", "pepper", "basil"],
        "steps": [
            {"text": "Boil pasta according to package instructions until al dente."},
            {"text": "Heat olive oil in a pan, sauté chopped onion until translucent."},
            {"text": "Add minced garlic and cook 30 seconds."},
            {"text": "Add chopped tomatoes, simmer 10-15 minutes until sauce thickens."},
            {"text": "Mix pasta with sauce, season with salt, pepper and fresh basil. Serve."}
        ],
        "metadata": {"servings": 2}
    },
    {
        "id": 2,
        "name": "Egg Fried Rice",
        "type": "rice",
        "ingredients": ["rice", "carrot", "peas", "egg", "onion", "soy sauce", "oil", "salt", "pepper"],
        "steps": [
            {"text": "Cook rice and leave it to cool (preferably use day-old rice)."},
            {"text": "Heat oil in a wok, scramble egg and set aside."},
            {"text": "Sauté onion, add carrots and peas until tender."},
            {"text": "Add rice, soy sauce and stir-fry until well mixed. Add scrambled egg back in."},
            {"text": "Season with salt and pepper and serve hot."}
        ],
        "metadata": {"servings": 3}
    },
    {
    "id": 3,
    "name": "Vegetable Fried Rice",
    "type": "rice",
    "ingredients": ["rice", "carrot", "peas", "onion", "soy sauce", "oil", "garlic", "salt", "pepper"],
    "steps": [
        {"text": "Heat oil in a pan and sauté chopped onions until soft."},
        {"text": "Add minced garlic and cook for 30 seconds."},
        {"text": "Add chopped carrot and peas; stir-fry for 3–4 minutes."},
        {"text": "Add cooked rice and mix well."},
        {"text": "Add soy sauce, salt, and pepper; stir-fry for another 2 minutes."}
    ],
    "metadata": {"servings": 2}
},
{
    "id": 4,
    "name": "Garlic Butter Chicken",
    "type": "chicken",
    "ingredients": ["chicken", "garlic", "butter", "salt", "pepper", "lemon juice", "parsley"],
    "steps": [
        {"text": "Season chicken with salt and pepper."},
        {"text": "Heat butter in a pan and sear chicken until golden."},
        {"text": "Add minced garlic and cook until fragrant."},
        {"text": "Squeeze lemon juice over chicken and simmer for 5 minutes."},
        {"text": "Garnish with chopped parsley and serve."}
    ],
    "metadata": {"servings": 3}
},
{
    "id": 5,
    "name": "Masala Egg Bhurji",
    "type": "egg",
    "ingredients": ["egg", "onion", "tomato", "turmeric", "salt", "chili powder", "oil", "coriander"],
    "steps": [
        {"text": "Heat oil and sauté chopped onions until golden."},
        {"text": "Add chopped tomatoes and cook until soft."},
        {"text": "Add turmeric, chili powder, and salt; mix well."},
        {"text": "Pour beaten eggs and scramble until cooked."},
        {"text": "Garnish with coriander and serve hot."}
    ],
    "metadata": {"servings": 2}
},
{
    "id": 6,
    "name": "Simple Vegetable Curry",
    "type": "curry",
    "ingredients": ["potato", "carrot", "peas", "onion", "tomato", "garlic", "turmeric", "salt", "oil", "garam masala"],
    "steps": [
        {"text": "Heat oil and sauté onions until golden."},
        {"text": "Add garlic and cook for 30 seconds."},
        {"text": "Add tomatoes and cook into a soft paste."},
        {"text": "Add chopped vegetables, turmeric, and salt; mix well."},
        {"text": "Add water, cover, and simmer until vegetables are cooked."},
        {"text": "Finish with garam masala and serve."}
    ],
    "metadata": {"servings": 3}
},
{
    "id": 7,
    "name": "Classic Pancakes",
    "type": "dessert",
    "ingredients": ["flour", "milk", "egg", "butter", "sugar", "baking powder", "salt"],
    "steps": [
        {"text": "Mix flour, sugar, baking powder, and salt in a bowl."},
        {"text": "Whisk milk, egg, and melted butter together."},
        {"text": "Combine wet and dry ingredients to form a smooth batter."},
        {"text": "Heat a pan and pour batter; cook both sides until golden."},
        {"text": "Serve with syrup or fruit."}
    ],
    "metadata": {"servings": 4}
},
{
    "id": 8,
    "name": "Chickpea Salad",
    "type": "salad",
    "ingredients": ["chickpeas", "tomato", "onion", "cucumber", "lemon juice", "salt", "pepper", "olive oil"],
    "steps": [
        {"text": "Rinse chickpeas and add to a bowl."},
        {"text": "Add chopped tomato, onion, and cucumber."},
        {"text": "Season with salt and pepper."},
        {"text": "Add lemon juice and olive oil; mix well."},
        {"text": "Serve chilled."}
    ],
    "metadata": {"servings": 2}
},
{
    "id": 9,
    "name": "Creamy Mushroom Soup",
    "type": "soup",
    "ingredients": ["mushroom", "onion", "garlic", "butter", "milk", "salt", "pepper"],
    "steps": [
        {"text": "Melt butter and sauté onions and garlic until soft."},
        {"text": "Add sliced mushrooms and cook until tender."},
        {"text": "Add milk and simmer for 10 minutes."},
        {"text": "Blend until smooth, then reheat and season with salt and pepper."},
        {"text": "Serve warm."}
    ],
    "metadata": {"servings": 2}
},
{
    "id": 10,
    "name": "Lemon Rice",
    "type": "rice",
    "ingredients": ["rice", "lemon", "turmeric", "oil", "salt", "mustard seeds", "curry leaves"],
    "steps": [
        {"text": "Heat oil and splutter mustard seeds."},
        {"text": "Add curry leaves and turmeric; mix well."},
        {"text": "Add cooked rice and combine thoroughly."},
        {"text": "Squeeze fresh lemon juice and mix."},
        {"text": "Serve with pickle or yogurt."}
    ],
    "metadata": {"servings": 2}
},
{
    "id": 11,
    "name": "Simple Chicken Curry",
    "type": "chicken",
    "ingredients": ["chicken", "onion", "tomato", "garlic", "ginger", "turmeric", "salt", "chili powder", "oil"],
    "steps": [
        {"text": "Heat oil and sauté onions until golden."},
        {"text": "Add garlic and ginger; cook until fragrant."},
        {"text": "Add tomatoes and cook until softened."},
        {"text": "Add chicken and spices; mix well."},
        {"text": "Add water and simmer until chicken is cooked through."}
    ],
    "metadata": {"servings": 3}
},
{
    "id": 12,
    "name": "Stir-Fried Noodles",
    "type": "noodles",
    "ingredients": ["noodles", "carrot", "capsicum", "onion", "soy sauce", "oil", "garlic", "salt", "pepper"],
    "steps": [
        {"text": "Boil noodles and set aside."},
        {"text": "Stir-fry vegetables in hot oil for 2–3 minutes."},
        {"text": "Add garlic and cook briefly."},
        {"text": "Add noodles, soy sauce, salt, and pepper; toss well."},
        {"text": "Serve hot."}
    ],
    "metadata": {"servings": 2}
},

]

# substitution mapping (simple)
substitutions = {
    "butter": ["olive oil", "margarine"],
    "milk": ["soy milk", "almond milk", "water"],
    "egg": ["tofu scramble", "chia seed + water (1 tbsp chia + 3 tbsp water)"],
    "soy sauce": ["tamari", "coconut aminos"],
    "pasta": ["spaghetti", "penne"],
    "tomato": ["tomato puree", "canned tomato", "sundried tomato (rehydrate)"],
    "rice": ["quinoa", "cauliflower rice"],
    "garlic": ["garlic powder (small amount)", "shallot"]
}

conn = sqlite3.connect(DB)
c = conn.cursor()

# create tables
c.execute('''
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY,
    name TEXT,
    type TEXT,
    ingredients TEXT,
    steps TEXT,
    metadata TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS substitutions (
    ingredient TEXT PRIMARY KEY,
    substitutes TEXT
)
''')

# insert recipes
for r in recipes:
    c.execute('INSERT OR REPLACE INTO recipes (id, name, type, ingredients, steps, metadata) VALUES (?,?,?,?,?,?)',
              (r["id"], r["name"], r["type"], json.dumps(r["ingredients"]), json.dumps(r["steps"]), json.dumps(r["metadata"])))

# insert subs
for k, v in substitutions.items():
    c.execute('INSERT OR REPLACE INTO substitutions (ingredient, substitutes) VALUES (?,?)', (k, json.dumps(v)))

conn.commit()
conn.close()
print("Created recipes.db with sample data.")
