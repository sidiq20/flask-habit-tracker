import os
from enum import unique
from flask import Flask
from routes import pages
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.register_blueprint(pages)

    try:
        mongo_uri = os.environ.get("MONGO_URI")
        if not mongo_uri:
            raise RuntimeError("MONGO_URI is not set in the environment variables.")

        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()

        db_name = os.environ.get("DB_NAME", "tracker")  # Default to "tracker" if not set
        app.db = client[db_name]
        app.db.habits.create_index([("added", 1)])
        app.db.completions.create_index([("date", 1), ("habit", 1)], unique=True)

    except Exception as e:
        raise RuntimeError(f"Failed to connect to MongoDB: {str(e)}")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=3000)
