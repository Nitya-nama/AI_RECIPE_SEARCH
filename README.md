# AI_RECIPE_SEARCH

A smart recipe search web app built with **Flask**, **MongoDB**, and **AI semantic search**.  
Automatically loads **500+ recipes** on the first run.

---

## 🚀 Features

- **Add Recipes** with ingredients, steps, cuisine, difficulty, and tags  
- **Ingredient-Based Search** (include/exclude filters)  
- **Semantic AI Search** using MiniLM embeddings  
- **500 Preloaded Recipes** auto-inserted into MongoDB  
- **Dark/Light Mode Toggle** (UI theme switch)  
- **Refresh Button** (clears all forms and results instantly)  
- **History Page** to view all saved recipes  

---

## 🛠️ Technologies Used

- Flask (Python)
- MongoDB Atlas
- SentenceTransformer MiniLM  
- HTML, CSS, JavaScript (Fetch API)

---

## 📦 Setup Instructions

### 1. Install dependencies:
```bash
pip install -r requirements.txt
````

### 2. Add your MongoDB credentials in `.env`:

```env
MONGODB_URI="your-connection-string"
DB_NAME="recipe_search_db"
```

### 3. Run the app:

```bash
python app.py
```

### 4. Open in browser:

```
http://127.0.0.1:5000/
```

---

## 📁 Project Structure

```
app.py
config.py
model.py
extended_500_recipes.json
templates/
static/
```

---

## 🔍 API Routes

* `POST /api/recipes` — Add recipe
* `GET /api/recipes/search-ingredients` — Filter by ingredients
* `GET /api/recipes/search-semantic` — AI semantic search
* `GET /history` — View saved recipes

---
