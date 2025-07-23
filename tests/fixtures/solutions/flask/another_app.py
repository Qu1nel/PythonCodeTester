from flask import Flask, request, jsonify
from typing import Dict, List, Any

app = Flask(__name__)

users_db: List[Dict[str, Any]] = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 25},
]

posts_db: List[Dict[str, Any]] = [
    {"id": 1, "title": "First Post", "content": "Hello World!", "author_id": 1},
    {"id": 2, "title": "Second Post", "content": "Flask is great!", "author_id": 2},
]


@app.route("/")
def home():
    return {"message": "Welcome to Simple API", "version": "1.0"}


@app.route("/users", methods=["GET"])
def get_users():
    return {"users": users_db}


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return {"error": "User not found"}, 404
    return {"user": user}


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    
    if not data or "name" not in data or "email" not in data:
        return {"error": "Name and email are required"}, 400
    
    new_id = max(u["id"] for u in users_db) + 1 if users_db else 1
    new_user = {
        "id": new_id,
        "name": data["name"],
        "email": data["email"],
        "age": data.get("age", 0)
    }
    
    users_db.append(new_user)
    return {"user": new_user}, 201


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id: int):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return {"error": "User not found"}, 404
    
    data = request.get_json()
    if not data:
        return {"error": "No data provided"}, 400
    
    user.update(data)
    return {"user": user}


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    global users_db
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return {"error": "User not found"}, 404
    
    users_db = [u for u in users_db if u["id"] != user_id]
    return {"message": "User deleted successfully"}


@app.route("/posts", methods=["GET"])
def get_posts():
    author_id = request.args.get("author_id", type=int)
    if author_id:
        filtered_posts = [p for p in posts_db if p["author_id"] == author_id]
        return {"posts": filtered_posts}
    return {"posts": posts_db}


@app.route("/posts", methods=["POST"])
def create_post():
    data = request.get_json()
    
    required_fields = ["title", "content", "author_id"]
    if not data or not all(field in data for field in required_fields):
        return {"error": "Title, content, and author_id are required"}, 400
    
    author = next((u for u in users_db if u["id"] == data["author_id"]), None)
    if not author:
        return {"error": "Author not found"}, 400
    
    new_id = max(p["id"] for p in posts_db) + 1 if posts_db else 1
    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"],
        "author_id": data["author_id"]
    }
    
    posts_db.append(new_post)
    return {"post": new_post}, 201


if __name__ == "__main__":
    app.run(debug=True)