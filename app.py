from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return render_template('index.html')


# =========================
# PASTA RECIPE API
# =========================
@app.route('/api/recipe', methods=['POST'])
def recipe():

    data = request.json

    ingredients = [i.lower().strip() for i in data.get('ingredients', [])]
    pasta_type = data.get('desired_type', '').lower()

    pasta_recipes = [

        {
            "name": "White Sauce Pasta",
            "type": "white sauce pasta",
            "ingredients_required": ["pasta", "milk", "cheese", "butter", "garlic"],
            "steps": [
    "Boil pasta until soft.",
    "Prepare white sauce using butter, milk, and cheese.",
    "Mix pasta with sauce and serve hot."
]
        },

        {
            "name": "Red Sauce Pasta",
            "type": "red sauce pasta",
            "ingredients_required": ["pasta", "tomato", "garlic", "onion", "chilli flakes"],
            "steps": [
    "Boil pasta properly.",
    "Cook tomato sauce with garlic and onion.",
    "Mix sauce with pasta and add chilli flakes."
]        },

        {
            "name": "Cheesy Pasta",
            "type": "cheesy pasta",
            "ingredients_required": ["pasta", "cheese", "milk", "oregano"],
            "steps": [
    "Boil pasta.",
    "Melt cheese with milk.",
    "Mix pasta and cheese sauce together."
]        },

        {
            "name": "Spicy Veg Pasta",
            "type": "spicy veg pasta",
            "ingredients_required": ["pasta", "capsicum", "tomato", "chilli sauce"],
            "steps": [
    "Boil pasta.",
    "Cook vegetables with chilli sauce.",
    "Add pasta and mix well."
]        }

    ]

    matched = []

    for recipe in pasta_recipes:

        if pasta_type == recipe["type"]:

            missing = [
                item for item in recipe["ingredients_required"]
                if item not in ingredients
            ]

            matched.append({
                "name": recipe["name"],
                "type": recipe["type"],
                "missing_ingredients": missing,
                "steps": recipe["steps"]
            })

    return jsonify({
        "candidates": matched
    })


# =========================
# CHATBOT API
# =========================
@app.route('/chatbot', methods=['POST'])
def chatbot():

    data = request.json
    user_message = data.get('message', '').lower()

    pasta_facts = [

        "Italy has more than 350 different pasta shapes 🍝",
        "Pasta was first made over 1000 years ago.",
        "Cheese pasta is one of the world's favorite comfort foods 🧀",
        "White sauce pasta is made using béchamel sauce.",
        "Tomato pasta sauce became popular in Italy during the 18th century."

    ]

    response = "Sorry, I only answer pasta-related questions 🍝"

    # Greeting
    if any(word in user_message for word in ['hello', 'hi', 'hey']):

        response = (
            "Hello 👋 I am Smart Pasta Chatbot 🍝\n\n"
            "You can ask me:\n"
            "• White sauce pasta\n"
            "• Red sauce pasta\n"
            "• Cheesy pasta\n"
            "• Spicy pasta\n"
            "• Healthy pasta\n"
            "• Pasta ingredients\n"
            "• Pasta facts\n"
            "• Pasta jokes\n"
            "• Lunch ideas\n"
            "• Dinner ideas\n"
            "• Italian pasta\n"
            "• Pasta sauce\n"
            "• Cooking pasta\n"
            "• Cheese used in pasta"
        )

    # Name
    elif 'your name' in user_message:
        response = "I am Smart Pasta Chatbot 🍝"

    # White Sauce Pasta
    elif 'white sauce pasta' in user_message:

        response = (
            "🍝 White Sauce Pasta Recipe:\n\n"
            "1. Boil pasta.\n"
            "2. Prepare sauce using butter, milk, and cheese.\n"
            "3. Mix pasta with sauce.\n"
            "4. Serve hot."
        )

    # Red Sauce Pasta
    elif 'red sauce pasta' in user_message:

        response = (
            "🍅 Red Sauce Pasta Recipe:\n\n"
            "1. Boil pasta.\n"
            "2. Cook tomato sauce with garlic and onion.\n"
            "3. Mix pasta with sauce.\n"
            "4. Add chilli flakes."
        )

    # Cheesy Pasta
    elif 'cheesy pasta' in user_message:

        response = (
            "🧀 Cheesy Pasta Recipe:\n\n"
            "1. Boil pasta.\n"
            "2. Melt cheese with milk.\n"
            "3. Mix together.\n"
            "4. Serve creamy pasta hot."
        )

    # Spicy Pasta
    elif 'spicy pasta' in user_message:

        response = (
            "🌶️ Spicy Pasta Recipe:\n\n"
            "1. Boil pasta.\n"
            "2. Cook vegetables with chilli sauce.\n"
            "3. Add pasta.\n"
            "4. Mix well and serve."
        )

    # Healthy Pasta
    elif 'healthy pasta' in user_message:

        response = (
            "🥗 Healthy Pasta Tips:\n\n"
            "• Use wheat pasta\n"
            "• Add vegetables\n"
            "• Use olive oil\n"
            "• Use low-fat cheese"
        )

    # Ingredients
    elif 'ingredient' in user_message:

        response = (
            "🍝 Common Pasta Ingredients:\n\n"
            "• Pasta\n"
            "• Cheese\n"
            "• Garlic\n"
            "• Tomato\n"
            "• Oregano\n"
            "• Butter\n"
            "• Milk"
        )

    # Italian Pasta
    elif 'italian' in user_message:

        response = (
            "🇮🇹 Italian Pasta:\n\n"
            "Pasta is one of the most famous Italian foods.\n"
            "Popular Italian pastas include Alfredo, Penne Arrabbiata, and Spaghetti."
        )

    # Cheese
    elif 'cheese' in user_message:

        response = (
            "🧀 Cheese Used In Pasta:\n\n"
            "• Mozzarella\n"
            "• Parmesan\n"
            "• Cheddar\n"
            "• Ricotta"
        )

    # Sauce
    elif 'sauce' in user_message:

        response = (
            "🍅 Popular Pasta Sauces:\n\n"
            "• White sauce\n"
            "• Red sauce\n"
            "• Alfredo sauce\n"
            "• Pesto sauce"
        )

    # Cook Pasta
    elif 'cook pasta' in user_message:

        response = (
            "🍝 Cooking Pasta:\n\n"
            "Boil pasta in salted water for 8 to 12 minutes."
        )

    # Pasta Fact
    elif 'fact' in user_message:
        response = random.choice(pasta_facts)

    # Lunch
    elif 'lunch' in user_message:

        response = (
            "🍝 Pasta Lunch Ideas:\n\n"
            "• Red sauce pasta\n"
            "• Spicy veg pasta\n"
            "• Cheesy pasta"
        )

    # Dinner
    elif 'dinner' in user_message:

        response = (
            "🍝 Pasta Dinner Ideas:\n\n"
            "• White sauce pasta\n"
            "• Cheesy pasta\n"
            "• Garlic pasta"
        )

    # Joke
    elif 'joke' in user_message:

        response = random.choice([
            "What do you call fake spaghetti? 🍝 An impasta 😂",
            "Why did the pasta visit the doctor? Because it felt saucy 😂",
            "What type of pasta is smartest? Thinkghetti 🤓🍝"
        ])

    # Motivation
    elif 'motivation' in user_message:

        response = "🍝 Keep calm and eat pasta."

    # Thanks
    elif any(word in user_message for word in ['thank', 'thanks']):

        response = "You're welcome 🍝"

    # Bye
    elif any(word in user_message for word in ['bye', 'goodbye']):

        response = "Goodbye 👋 Enjoy your pasta 🍝"

    return jsonify({
        'reply': response
    })


if __name__ == '__main__':
    app.run(debug=True)