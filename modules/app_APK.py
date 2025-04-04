from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import string
from flask import Blueprint
app_APK = Blueprint('app_APK', __name__, url_prefix='/apk')

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['shortly']
collection = db['urls']

# In-memory storage for URL mappings
url_mapping = {}
base_url="https://short.ly/"

def generate_short_code():
    """Generate a random 6-character alphanumeric short code."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/bulk-shorten', methods=['POST'])
def bulk_shorten():
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

            created_at = datetime.utcnow()
            record = {"shortCode": short_code,
                "longUrl": url,
                "createdAt":created_at ,
                "expiryDate": created_at + timedelta(days=90),
                "clicks": 0}
            collection.insert_one(record)

        shortened_urls.append({
            'longUrl': url,
            'shortUrl': base_url + short_code,
            'shortCode': short_code
        })
    return jsonify({'shortUrls': shortened_urls})

if __name__ == '__main__':
    app.run(debug=True)
