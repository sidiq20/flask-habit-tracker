from datetime import datetime
from enum import unique
from typing import Optional
from pymongo import MongoClient
from bson import ObjectId
import os
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    def __init__(self):
        self.client = MongoClient(os.environ.get('MONGO_URI'))
        self.db = self.client[os.environ.get('DB_NAME', 'habit_tracker')]

        self.db.users.create_index('email', unique=True)
        self.db.habits.create_index([('userId', 1), ('name', 1)])
        self.db.completions.create_index([('habitId', 1), ('date', 1)], unique=True)

    def create_user(self, email: str, password: str, timezone: str = 'UTC') -> Optional[dict]:
        try:
            user = {
                'email': email.lower(),
                'password': generate_password_hash(password),
                'timezone': timezone,
                'create': datetime.utcnow()
            }