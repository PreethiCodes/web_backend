from flask import Flask, request, jsonify,Blueprint
from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import string
from dotenv import load_dotenv
import os

load_dotenv()
# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['shortly']
collection = db['urls']

class BSModule:
    def __init__(self):
        self.bp = Blueprint('bs', __name__, url_prefix='/bs')
        self.register_routes()
    def register_routes(self):
        """Register routes for the bulk shorten module."""
        @self.bp.route('/bulk-shorten', methods=['POST'])
        
        def bulk_shorten():
            #TODO CH4 change the base_url, frontend team should provide this once they decide
            # In-memory storage for URL mappings
            url_mapping = {}
            base_url="https://short.ly/"

            def generate_short_code():
                """Generate a random 6-character alphanumeric short code."""
                return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

            """Bulk shorten URLs."""
            data = request.json
            if not data or 'urls' not in data:
                return jsonify({'error': 'Invalid request. Provide a list of URLs under "urls" key.'}), 400

            urls = data['urls']
            if not isinstance(urls, list):
                return jsonify({'error': '"urls" should be a list.'}), 400
            #urls is a list of long urls
            
            shortened_urls = []
            for url in urls:
                if not url.startswith("http://") and not url.startswith("https://"):
                    return jsonify({"error": f"Invalid URL: {url}"}), 400
                if url in url_mapping:
                    short_code = url_mapping[url]
                else:
                    short_code = generate_short_code()
                    while short_code in url_mapping.values():  # Ensure unique short codes
                        short_code = generate_short_code()
                    url_mapping[url] = short_code
                    url_mapping[short_code] = url  # Reverse mapping for retrieval

                    created_at = datetime.utcnow().isoformat()
                    expiry_date = (datetime.utcnow() + timedelta(days=90)).isoformat()
                    record = {"shortCode": short_code,
                        "longUrl": url,
                        "createdAt":created_at ,
                        "expiryDate": expiry_date,
                        "clicks": 0}
                    collection.insert_one(record)

                shortened_urls.append({
                    'longUrl': url,
                    'shortUrl': base_url + short_code,
                    'shortCode': short_code
                })
            return jsonify({'shortUrls': shortened_urls})

    def get_blueprint(self):
        return self.bp
