from pymongo import MongoClient

# 👉 CHANGE THIS URI IF NEEDED (use your working cluster)
MONGO_URI = "mongodb+srv://flaskuser:flaskuser@cluster0.evdx1pz.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)

# Database & collection for recipes
db = client["recipe_search_db"]
recipes_collection = db["recipes"]
