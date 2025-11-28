from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

from config import recipes_collection
from model import get_embedding, cosine_similarities

app = Flask(__name__)


# ===============================================================
# 🔥 AUTO-LOAD 500 REAL RECIPES INTO MONGODB
# ===============================================================
def load_initial_recipes():
    """Loads 500 recipes from the JSON file into MongoDB once."""

    try:
        # If recipes already exist, SKIP loading
        if recipes_collection.count_documents({}) > 0:
            print("ℹ️ Recipes already exist in MongoDB. Skipping autoload.")
            return

        # Confirm file exists
        if not os.path.exists("extended_500_recipes.json"):
            print("❌ Dataset file extended_500_recipes.json not found!")
            return

        print("⏳ Loading 500-recipe dataset...")

        # Load JSON file
        with open("extended_500_recipes.json", "r", encoding="utf-8") as f:
            recipes = json.load(f)

        print(f"📦 {len(recipes)} recipes loaded from JSON.")

        # Insert each recipe with embedding
        inserted_count = 0

        for r in recipes:
            # Build embedding text for AI search
            ingredient_names = ", ".join(i["name"] for i in r["ingredients"])
            embedding_text = f"{r['title']}. {r['description']}. Cuisine: {r['cuisine']}. Ingredients: {ingredient_names}."

            r["embedding"] = get_embedding(embedding_text)
            r["created_at"] = datetime.utcnow()

            recipes_collection.insert_one(r)
            inserted_count += 1

        print(f"✅ Successfully inserted {inserted_count} recipes into MongoDB!")

    except Exception as e:
        print("❌ Auto-load failed:", e)


# ===============================================================
# 🏠 HOME PAGE
# ===============================================================
@app.route("/")
def index():
    return render_template("index.html")


# ===============================================================
# ➕ ADD NEW RECIPE (API)
# ===============================================================
@app.route("/api/recipes", methods=["POST"])
def add_recipe():
    data = request.get_json() or {}

    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    cuisine = (data.get("cuisine") or "").strip()
    difficulty = (data.get("difficulty") or "").strip()
    cook_time = data.get("cook_time")
    diet_tags_str = data.get("diet_tags") or ""
    diet_tags = [t.strip() for t in diet_tags_str.split(",") if t.strip()]

    ingredients_raw = data.get("ingredients") or []
    steps_raw = data.get("steps") or ""

    if not title:
        return jsonify({"error": "Title is required"}), 400

    # Parse ingredients
    ingredients = []
    if isinstance(ingredients_raw, list):
        for ing in ingredients_raw:
            name = (ing.get("name") or "").strip().lower()
            if not name:
                continue
            ingredients.append({
                "name": name,
                "quantity": (ing.get("quantity") or "").strip(),
                "unit": (ing.get("unit") or "").strip(),
            })

    # Steps list
    if isinstance(steps_raw, str):
        steps = [s.strip() for s in steps_raw.split("\n") if s.strip()]
    else:
        steps = [str(s).strip() for s in steps_raw if str(s).strip()]

    # Prepare embedding
    ingredient_names = ", ".join(i["name"] for i in ingredients)
    embedding_text = f"{title}. {description}. Cuisine: {cuisine}. Ingredients: {ingredient_names}."
    embedding = get_embedding(embedding_text)

    doc = {
        "title": title,
        "description": description,
        "cuisine": cuisine,
        "difficulty": difficulty,
        "cook_time": cook_time,
        "diet_tags": diet_tags,
        "ingredients": ingredients,
        "steps": steps,
        "embedding": embedding,
        "created_at": datetime.utcnow(),
    }

    result = recipes_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)

    return jsonify({"message": "Recipe added successfully!", "recipe": doc})


# ===============================================================
# 🔍 SEARCH BY INGREDIENTS (API)
# ===============================================================
@app.route("/api/recipes/search-ingredients", methods=["GET"])
def search_by_ingredients():
    include_str = request.args.get("include", "", type=str)
    exclude_str = request.args.get("exclude", "", type=str)
    cuisine = (request.args.get("cuisine", "") or "").strip()
    diet_tag = (request.args.get("diet_tag", "") or "").strip()

    include_ings = [s.strip().lower() for s in include_str.split(",") if s.strip()]
    exclude_ings = [s.strip().lower() for s in exclude_str.split(",") if s.strip()]

    query = {}
    if cuisine:
        query["cuisine"] = cuisine
    if diet_tag:
        query["diet_tags"] = {"$in": [diet_tag]}

    recipes = list(recipes_collection.find(query).sort("created_at", -1))

    filtered = []
    for r in recipes:
        ingredient_names = {i["name"].lower() for i in r.get("ingredients", [])}

        if include_ings and not all(ing in ingredient_names for ing in include_ings):
            continue

        if any(ing in ingredient_names for ing in exclude_ings):
            continue

        r["_id"] = str(r["_id"])
        filtered.append(r)

    return jsonify({"results": filtered, "count": len(filtered)})


# ===============================================================
# 🧠 SEMANTIC SEARCH (AI)
# ===============================================================
@app.route("/api/recipes/search-semantic", methods=["GET"])
def semantic_search():
    q = (request.args.get("q") or "").strip()

    if not q:
        return jsonify({"error": "Query 'q' is required"}), 400

    query_emb = get_embedding(q)
    if query_emb is None:
        return jsonify({"error": "Could not compute embedding"}), 500

    recipes = list(recipes_collection.find({}))

    if not recipes:
        return jsonify({"results": []})

    doc_embs = [r.get("embedding") for r in recipes]
    sims = cosine_similarities(query_emb, doc_embs)

    # Attach similarity scores
    for r, s in zip(recipes, sims):
        r["_id"] = str(r["_id"])
        r["similarity"] = round(float(s), 3)

    # Sort by similarity
    recipes.sort(key=lambda x: x.get("similarity", 0), reverse=True)

    return jsonify({"results": recipes, "count": len(recipes)})


# ===============================================================
# 📜 HISTORY PAGE
# ===============================================================
@app.route("/history")
def history():
    recipes = list(recipes_collection.find().sort("created_at", -1))
    for r in recipes:
        r["_id"] = str(r["_id"])
    return render_template("history.html", recipes=recipes)


# ===============================================================
# 🚀 RUN APP + AUTO-LOAD
# ===============================================================
if __name__ == "__main__":
    load_initial_recipes()   # Load 500 recipes automatically
    app.run(debug=True)
