from flask import Flask, jsonify, request 
import os 
 
app = Flask(__name__) 
 
@app.route('/healthz') 
def health(): 
    return jsonify({"status": "ok"}), 200 
 
@app.route('/dbcheck') 
def dbcheck(): 
    db_url = os.getenv('DATABASE_URL', 'not set') 
    return jsonify({"database": "connected" if db_url != 'not set' else "not configured"}), 200 
 
@app.route('/api/v1/products') 
def products(): 
    return jsonify({"message": "products endpoint working"}), 200 
 
if __name__ == '__main__': 
    port = int(os.getenv('PORT', 8080)) 
    app.run(host='0.0.0.0', port=port)
