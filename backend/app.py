
from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot.engine import MusicChatbot
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
KB_FILE = os.path.join(DATA_DIR, "knowledge_base.json")

app = Flask(__name__)
CORS(app)
bot = MusicChatbot(KB_FILE, PRODUCTS_FILE)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "app": "YM Music Store API"})

@app.get("/api/products")
def products():
    items = load_json(PRODUCTS_FILE)
    category = request.args.get("category")
    search = request.args.get("q", "").lower().strip()
    if category and category != "All":
        items = [p for p in items if p["category"] == category]
    if search:
        items = [p for p in items if search in (p["name"] + " " + p["category"] + " " + p["description"]).lower()]
    return jsonify(items)

@app.get("/api/categories")
def categories():
    items = load_json(PRODUCTS_FILE)
    return jsonify(["All"] + sorted({p["category"] for p in items}))

@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Message tidak boleh kosong"}), 400
    return jsonify(bot.reply(message))

@app.get("/api/admin/knowledge")
def get_knowledge():
    return jsonify(load_json(KB_FILE))

@app.put("/api/admin/knowledge")
def update_knowledge():
    payload = request.get_json(silent=True)
    if not isinstance(payload, list):
        return jsonify({"error": "Format knowledge base harus berupa array"}), 400
    save_json(KB_FILE, payload)
    bot.reload()
    return jsonify({"message": "Knowledge base berhasil diperbarui", "count": len(payload)})

@app.get("/api/admin/products")
def get_admin_products():
    return jsonify(load_json(PRODUCTS_FILE))

@app.put("/api/admin/products")
def update_products():
    payload = request.get_json(silent=True)
    if not isinstance(payload, list):
        return jsonify({"error": "Format katalog produk harus berupa array"}), 400
    required_fields = ("id", "name", "category", "price", "description")
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            return jsonify({"error": f"Produk ke-{index + 1} harus berupa object"}), 400
        missing = [field for field in required_fields if field not in item or item[field] in (None, "")]
        if missing:
            return jsonify({"error": f"Produk ke-{index + 1} belum memiliki field: {', '.join(missing)}"}), 400
        if not isinstance(item.get("specifications", {}), dict):
            return jsonify({"error": f"Spesifikasi produk ke-{index + 1} harus berupa object"}), 400
    save_json(PRODUCTS_FILE, payload)
    bot.reload()
    return jsonify({"message": "Katalog produk berhasil diperbarui", "count": len(payload)})

@app.get("/api/admin/stats")
def stats():
    products_data = load_json(PRODUCTS_FILE)
    knowledge = load_json(KB_FILE)
    return jsonify({
        "products": len(products_data),
        "knowledge": len(knowledge),
        "categories": len({p["category"] for p in products_data})
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
