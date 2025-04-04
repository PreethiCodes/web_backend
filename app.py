from flask import Flask
from modules import app_APK
from modules import app_sub
from modules import app_admin
from modules import app_pr
import os

app = Flask(__name__)

# Register blueprints with error handling
try:
    app.register_blueprint(app_APK)
    app.register_blueprint(app_sub)
    app.register_blueprint(app_pr)
    app.register_blueprint(app_admin)
except Exception as e:
    print(f"Error registering blueprint: {e}")
with app.app_context():
    print("🔍 Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(rule)

if __name__ == '__main__':
    # Use environment variables for debug mode and port
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    app.run(debug=debug_mode, port=port)
