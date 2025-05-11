

from flask import Flask
from modules.app_bs import BSModule
from modules.app_admin import AdminModule
from modules.app_analytics import AnalyticsModule
from modules.app_shorten import ShortenModule
from pymongo import MongoClient, errors
import os

class MainApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.register_modules()
        self.register_routes()

    def _mongo_connection(self):
        try:

            mongo_uri=os.getenv("MONGO_URI", "mongodb+srv://apk:T1GavQISQkGmIShw@cluster0.dpdv9hr.mongodb.net/")
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')   
            print("MongoDB Connection Successful")
            return client
        except errors.ServerSelectionTimeoutError as err:
            print("MongoDB connection timeout.")
            print(f"Details: {err}")
        except errors.OperationFailure as err:
            print("MongoDB authentication failed.")
            print(f"Details: {err}")
        except Exception as err:
            print("An unexpected MongoDB error occurred.")
            print(f"Details: {err}")
        return None

    def register_modules(self):
        self.app.register_blueprint(BSModule().get_blueprint())
        self.app.register_blueprint(AdminModule().get_blueprint())
        self.app.register_blueprint(AnalyticsModule().get_blueprint())
        self.app.register_blueprint(ShortenModule().get_blueprint())

    def register_routes(self):
        @self.app.route("/")
        def home():
            return "Welcome to the Main App!"
        
    def get_app(self):
        return self.app
    

# This code initializes a Flask application and registers multiple modules (blueprints) to it.
# Each module is defined in its own file within the `modules` directory.
# The `MainApp` class encapsulates the application setup, including the registration of blueprints.
# The `get_app` method returns the Flask application instance.    
