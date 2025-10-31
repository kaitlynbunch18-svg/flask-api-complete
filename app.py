from flask import Flask, jsonify, request
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import requests

app = Flask(__name__)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', '')
UPSTREAM_BASE = os.getenv('UPSTREAM_BASE', 'https://bunch-of-equipment-online.com')
X_API_KEY = os.getenv('X_API_KEY', '')

def get_engine():
    if not DATABASE_URL:
        return None
    # Add SSL mode for Railway Postgres
    db_url = DATABASE_URL
    if 'sslmode=' not in db_url:
        separator = '&' if '?' in db_url else '?'
        db_url = f"{db_url}{separator}sslmode=require"
    return create_engine(db_url, pool_pre_ping=True)

engine = get_engine() if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine) if engine else None

@app.route('/healthz')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/dbcheck')
def dbcheck():
    if not engine:
        return jsonify({"database": "not configured"}), 200
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({"database": "connected"}), 200
    except Exception as e:
        return jsonify({"database": "error", "message": str(e)}), 500

@app.route('/api/v1/products')
def get_products():
    try:
        response = requests.get(f"{UPSTREAM_BASE}/api/v1/products", timeout=60)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 502

@app.route('/api/v1/bulk-update-images', methods=['POST'])
def bulk_update_images():
    if not X_API_KEY or request.headers.get('X-API-Key') != X_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        payload = request.get_json(force=True)
        headers = {
            'X-API-Key': X_API_KEY,
            'Content-Type': 'application/json'
        }
        response = requests.post(
            f"{UPSTREAM_BASE}/api/v1/bulk-update-images",
            json=payload,
            headers=headers,
            timeout=120
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 502

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
