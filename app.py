from flask import Flask, jsonify, render_template, request, session
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "hangman-adventure-development-key-change-me")

# Original project's word lists and matching hints.
CATEGORIES = {
    "Animals": {
        "emoji": "🐾",
        "words": ["TIGER", "RABBIT", "ELEPHANT", "DOLPHIN", "BUTTERFLY", "KANGAROO", "GIRAFFE"],
        "hints": ["A big striped cat", "A small animal with long ears", "The largest land animal",
                  "A clever sea mammal", "An insect with colorful wings", "An animal that hops",
                  "A very tall animal"],
    },
    "Fruits": {
        "emoji": "🍎",
        "words": ["APPLE", "BANANA", "ORANGE", "PAPAYA", "PINEAPPLE", "WATERMELON", "STRAWBERRY"],
        "hints": ["A red or green crunchy fruit", "A long yellow fruit", "A citrus fruit",
                  "A tropical orange fruit", "A spiky tropical fruit", "A large summer fruit",
                  "A red fruit with tiny seeds"],
    },
    "Vegetables": {
        "emoji": "🥕",
        "words": ["CARROT", "POTATO", "TOMATO", "BROCCOLI", "SPINACH", "CUCUMBER", "PUMPKIN"],
        "hints": ["An orange root vegetable", "A popular starchy vegetable", "Often used in salads",
                  "A green tree-shaped vegetable", "A leafy green vegetable",
                  "A refreshing green vegetable", "A large orange vegetable"],
    },
    "Countries": {
        "emoji": "🌍",
        "words": ["INDIA", "JAPAN", "CANADA", "BRAZIL", "FRANCE", "AUSTRALIA", "GERMANY"],
        "hints": ["A country in South Asia", "An island country in East Asia", "Known for maple leaves",
                  "A country in South America", "A country known for the Eiffel Tower",
                  "A country and continent", "A country in central Europe"],
    },
    "Sports": {
        "emoji": "🏆",
        "words": ["CRICKET", "FOOTBALL", "TENNIS", "HOCKEY", "BADMINTON", "VOLLEYBALL"],
        "hints": ["A bat-and-ball sport", "A popular team sport", "A racket sport",
                  "Played with a stick and puck/ball", "A racket sport with a shuttlecock",
                  "A sport played over a net"],
    },
    "Technology": {
        "emoji": "💻",
        "words": ["COMPUTER", "KEYBOARD", "INTERNET", "ROBOTICS", "SOFTWARE", "DATABASE"],
        "hints": ["An electronic device", "Used to type", "A global network", "The study of robots",
                  "Programs used by a computer", "An organized collection of data"],
    },
    "Flowers": {
        "emoji": "🌸",
        "words": ["ROSE", "LOTUS", "TULIP", "JASMINE", "SUNFLOWER", "HIBISCUS"],
        "hints": ["A flower with thorns", "A flower that grows in water", "A cup-shaped spring flower",
                  "A fragrant white flower", "A tall flower that follows the sun",
                  "A colorful tropical flower"],
    },
    "Vehicles": {
        "emoji": "🚗",
        "words": ["CAR", "BICYCLE", "SCOOTER", "AIRPLANE", "HELICOPTER", "MOTORCYCLE"],
        "hints": ["A four-wheeled road vehicle", "A two-wheeled pedal vehicle", "A small two-wheeler",
                  "A flying vehicle with wings", "A flying vehicle with rotating blades",
                  "A powered two-wheeler"],
    },
}

LEVELS = {
    "easy": {"max_mistakes": 6, "filter": lambda word: len(word) <= 6},
    "medium": {"max_mistakes": 6, "filter": lambda word: 7 <= len(word) <= 9},
    "hard": {"max_mistakes": 5, "filter": lambda word: len(word) >= 10},
    # The original JavaScript version uses the full category pool for Expert,
    # but gives the player fewer chances.
    "expert": {"max_mistakes": 4, "filter": lambda word: True},
}

def public_state():
    word = session.get("word", "")
    guessed = session.get("guessed", [])
    category = session.get("category", "Animals")
    level = session.get("level", "easy")
    mistakes = session.get("mistakes", 0)
    max_mistakes = session.get("max_mistakes", 6)
    finished = session.get("finished", False)
    won = session.get("won", False)

    return {
        "category": category,
        "category_emoji": CATEGORIES.get(category, {}).get("emoji", "🎯"),
        "level": level,
        "word_length": len(word),
        "hint": session.get("hint", ""),
        "guessed": guessed,
        "mistakes": mistakes,
        "max_mistakes": max_mistakes,
        "lives": max(0, max_mistakes - mistakes),
        "finished": finished,
        "won": won,
        "word_display": [letter if letter in guessed else "" for letter in word],
        "answer": word if finished else "",
    }

def create_round(category, level):
    if category not in CATEGORIES:
        return False, "Please choose a valid category."
    if level not in LEVELS:
        return False, "Please choose a valid difficulty level."

    data = CATEGORIES[category]
    rule = LEVELS[level]
    pairs = [(word, hint) for word, hint in zip(data["words"], data["hints"])
             if rule["filter"](word)]
    # Match original behavior: if a category has no words at a selected length,
    # use its available words rather than preventing the game from starting.
    if not pairs:
        pairs = list(zip(data["words"], data["hints"]))
    word, hint = random.choice(pairs)

    session["category"] = category
    session["level"] = level
    session["word"] = word
    session["hint"] = hint
    session["guessed"] = []
    session["mistakes"] = 0
    session["max_mistakes"] = rule["max_mistakes"]
    session["finished"] = False
    session["won"] = False
    session.modified = True
    return True, "A new word is ready."

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/categories")
def categories():
    return jsonify({
        name: {"emoji": data["emoji"]}
        for name, data in CATEGORIES.items()
    })

@app.post("/api/start")
def start_game():
    payload = request.get_json(silent=True) or {}
    category = payload.get("category", "Animals")
    level = payload.get("level", "easy")
    ok, message = create_round(category, level)
    if not ok:
        return jsonify({"ok": False, "message": message}), 400
    return jsonify({"ok": True, "message": message, "state": public_state()})

@app.get("/api/state")
def game_state():
    if not session.get("word"):
        return jsonify({"ok": False, "message": "No active game."}), 404
    return jsonify({"ok": True, "state": public_state()})

@app.post("/api/guess")
def make_guess():
    if not session.get("word"):
        return jsonify({"ok": False, "message": "Start a new game first."}), 400
    payload = request.get_json(silent=True) or {}
    letter = str(payload.get("letter", "")).upper()
    if len(letter) != 1 or not letter.isalpha() or not letter.isascii():
        return jsonify({"ok": False, "message": "Please choose one English letter."}), 400
    guessed = session.get("guessed", [])
    if session.get("finished") or letter in guessed:
        return jsonify({"ok": True, "state": public_state()})

    guessed.append(letter)
    session["guessed"] = guessed
    if letter not in session["word"]:
        session["mistakes"] = session.get("mistakes", 0) + 1

    if all(char in guessed for char in session["word"]):
        session["finished"] = True
        session["won"] = True
    elif session["mistakes"] >= session["max_mistakes"]:
        session["finished"] = True
        session["won"] = False

    session.modified = True
    return jsonify({"ok": True, "state": public_state()})

@app.post("/api/new-round")
def new_round():
    category = session.get("category", "Animals")
    level = session.get("level", "easy")
    ok, message = create_round(category, level)
    return jsonify({"ok": ok, "message": message, "state": public_state()})

@app.post("/api/reset")
def reset_game():
    session.clear()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)
