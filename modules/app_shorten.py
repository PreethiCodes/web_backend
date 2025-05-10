from flask import Flask, request, jsonify, redirect
from pymongo import MongoClient
from datetime import datetime, timedelta
from flask import Blueprint
import os
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['shortly'] 
collection = db['urls']

class ShortenModule:
    def __init__(self):
        self.bp = Blueprint('shorten', __name__, url_prefix='/shorten')
        self.register_routes()
    def register_routes(self):
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

            created_at = datetime.utcnow().isoformat()
            expiry_date = (datetime.utcnow() + timedelta(days=90)).isoformat()
            record = {"shortCode": short_code,
                "longUrl": long_url,
                "createdAt":created_at ,
                "expiryDate": expiry_date,
                "clicks": 0,
                "impressions": 0
            }

            collection.insert_one(record)
            short_url = f"http://short.ly/{short_code}"
            return jsonify({
                "shortUrl": short_url,
                "shortCode": short_code,
                "longUrl": long_url,
                "createdAt": record["createdAt"],
                "expiryDate": record["expiryDate"]
            }), 201

        @self.bp.route('/expand/<string:short_code>', methods=['GET'])
        def expand_url(short_code):
            result = collection.find_one({"shortCode": short_code})
            if not result:
                return jsonify({"error": "404 Not Found – Short code does not exist"}), 404
            expiry_date = result.get("expiryDate")
            if expiry_date and isoparse(expiry_date) < datetime.utcnow():
                return jsonify({"error": "410 Gone – URL has expired"}), 410
            return jsonify({
                "longUrl": result["longUrl"],
                "shortCode": result["shortCode"],
                "clicks": result["clicks"],
                "createdAt": result["createdAt"],
                "expiryDate": result["expiryDate"]
            })

        @self.bp.route('/<string:short_code>', methods=['GET'])
        def redirect_to_original_url(short_code):
            #* CH7 we wont need this, frontend will handle this
            record = collection.find_one({"shortCode": short_code})
            if not record:
                return jsonify({"error": "Short code does not exist"}), 404

    def get_blueprint(self):
        return self.bp
