import os
from flask import Flask
from routes import pages
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(pages)

    # Check if MONGO_URI is loaded
    mongo_uri = os.environ.get("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI is not set in the environment variables.")

    client = MongoClient(mongo_uri)
    db_name = os.environ.get("DB_NAME", "tracker")  # Default to "tracker" if not set
    app.db = client[db_name]

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=3000)
