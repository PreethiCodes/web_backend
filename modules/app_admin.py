from flask import Blueprint, request
from pymongo import MongoClient
from datetime import datetime

# Initialize Blueprint
app_admin = Blueprint('app_admin', __name__)

# Configure MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['shortly']
collection = db['urls']

@app_admin.route('/delete', methods=['DELETE'])
def delete_short_url():
    data = request.json
    if not data:
        return 'No data provided', 400

    short_code = data.get('shortCode')
    if not short_code:
        return 'No short URL code provided', 400

    result = collection.delete_one({'shortCode': short_code})
    if result.deleted_count == 0:
        return 'Short URL not found in the database', 404

    return 'Short URL deleted successfully', 200

@app_admin.route('/update/expiry', methods=['PATCH'])
def update_expiry():
    data = request.json
    if not data:
        return 'No data provided', 400

    short_code = data.get('shortCode')
    new_expiration = data.get('expiryAt')

    if not short_code:
        return 'No short URL code provided', 400
    if not new_expiration:
        return 'No expiration date provided', 400

    try:
        new_expiration_date = datetime.fromisoformat(new_expiration).isoformat()
    except ValueError:
        return 'Invalid expiration date format. Use ISO 8601 format (YYYY-MM-DD).', 400

    existing_entry = collection.find_one({'shortCode': short_code})
    if not existing_entry:
        return 'Short URL not found in the database', 404

    current_expiration = existing_entry.get('expiryAt')
    if current_expiration:
        try:
            current_expiration_date = datetime.fromisoformat(current_expiration)
        except ValueError:
            return 'Invalid current expiration date format in the database.', 500

        if current_expiration_date > datetime.now():
            return 'The current expiration date is still valid.', 200

    result = collection.update_one(
        {'shortCode': short_code},
        {'$set': {'expiryAt': new_expiration}}
    )

    if result.matched_count == 0:
        return 'Short URL not found in the database', 404

    return 'Expiration date updated successfully', 200
