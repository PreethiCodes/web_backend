from flask import Flask, request, jsonify, redirect
from pymongo import MongoClient
from datetime import datetime, timedelta
from flask import Blueprint
import os
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection
client = MongoClient('os.getenv('MONGODB_URI')')
db = client['shortly'] 
collection = db['urls']

class ShortenModule:
    def __init__(self):
        self.bp = Blueprint('shorten', __name__, url_prefix='/shorten')
        self.register_routes()

    # Generate a short code 
    def generate_short_code():
        from random import choices
        import string
        return ''.join(choices(string.ascii_letters + string.digits, k=6))

    @self.bp.route('/shorten', methods=['POST'])
    def shorten_url():
        data = request.json
        long_url = data.get('longUrl')
        custom_alias = data.get('customAlias')

        if not long_url:
            return jsonify({"error": "Long URL is required"}), 400

        # Check for custom alias
        if custom_alias:
            if collection.find_one({"shortCode": custom_alias}):
                return jsonify({"error": "Custom alias already in use"}), 400
            short_code = custom_alias
        else:
            short_code = generate_short_code()

        created_at = datetime.utcnow()
        record = {"shortCode": short_code,
            "longUrl": long_url,
            "createdAt":created_at ,
            "expiryDate": created_at + timedelta(days=90),
            "clicks": 0
        }

        collection.insert_one(record)
        short_url = f"http://short.ly/{short_code}"
        return jsonify({
            "shortUrl": short_url,
            "shortCode": short_code,
            "longUrl": long_url,
            "createdAt": record["createdAt"].isoformat(),
            "expiryDate": record["expiryDate"].isoformat()
        }), 201

    @self.bp.route('/expand/<string:short_code>', methods=['GET'])
    def expand_url(short_code):
        record = collection.find_one({"shortCode": short_code})
        if not record:
            return jsonify({"error": "Short code does not exist"}), 404
        
        # Check expiry
        if record['expiryDate'] < datetime.utcnow():
            return jsonify({"error": "URL has expired"}), 410

        return jsonify({
            "longUrl": record['longUrl'],
            "shortCode": short_code,
            "clicks": record['clicks'],
            "createdAt": record['createdAt'].isoformat(),
            "expiryDate": record['expiryDate'].isoformat()
        }), 200

    @self.bp..route('/<string:short_code>', methods=['GET'])
    def redirect_to_original_url(short_code):
        record = collection.find_one({"shortCode": short_code})
        if not record:
            return jsonify({"error": "Short code does not exist"}), 404
        
        # Update click count
        collection.update_one({"shortCode": short_code}, {"$inc": {"clicks": 1}})
        return redirect(record['longUrl'])

    def get_blueprint(self):
            return self.bp
