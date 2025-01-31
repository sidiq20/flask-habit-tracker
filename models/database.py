from datetime import datetime
from typing import Optional
from pymongo import MongoClient
from bson import ObjectId
import os
from werkzeug.security import generate_password_hash, check_password_hash


class Database:
    def __init__(self):
        self.client = MongoClient(os.environ.get('MONGO_URI'))
        self.db = self.client[os.environ.get('DB_NAME', 'habit_tracker')]

        # Create indexes
        # self.db.users.create_index('email', unique=True)
        # self.db.habits.create_index([('userId', 1), ('name', 1)])
        # self.db.completions.create_index([('habitId', 1), ('date', 1)], unique=True)

    def create_user(self, email: str, password: str, timezone: str = 'UTC') -> Optional[dict]:
        try:
            user = {
                'email': email.lower(),
                'password': generate_password_hash(password),
                'timezone': timezone,
                'createdAt': datetime.utcnow()
            }
            result = self.db.users.insert_one(user)
            user['_id'] = result.inserted_id
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[dict]:
        return self.db.users.find_one({'email': email.lower()})

    def verify_password(self, user: dict, password: str) -> bool:
        return check_password_hash(user['password'], password)

    def create_habit(self, user_id: str, name: str, reminder_time: str = '19:00') -> Optional[dict]:
        try:
            print(f"Saving habit for user: {user_id}, Habit: {name}")
            habit = {
                'userId': ObjectId(user_id),
                'name': name.strip(),
                'reminderTime': reminder_time,
                'createdAt': datetime.utcnow(),
                'lastReminderSent': None
            }
            result = self.db.habits.insert_one(habit)
            print(f"Habit saved with ID: {result.inserted_id}")
            habit['_id'] = result.inserted_id
            return habit
        except Exception as e:
            print(f"Error creating habit: {e}")
            return None

    def get_user_habits(self, user_id: str) -> list:
        print(f"Fetching habits for user: {user_id}")  # Debugging
        habits = list(self.db.habits.find({'userId': ObjectId(user_id)}))
        print(f"Found habits: {habits}")  # Debugging
        return habits

    def complete_habit(self, habit_id: str, date: datetime) -> bool:
        try:
            self.db.completions.insert_one({
                'habitId': ObjectId(habit_id),
                'date': date,
                'createdAt': datetime.utcnow()
            })
            return True
        except Exception as e:
            print(f"Error completing habit: {e}")
            return False

    def get_completion(self, habit_id: str, date: datetime) -> Optional[dict]:
        return self.db.completions.find_one({
            'habitId': ObjectId(habit_id),
            'date': date
        })

    def get_habits_needing_reminder(self, current_time: str) -> list:
        pipeline = [
            {
                '$match': {
                    'reminderTime': current_time,
                    '$or': [
                        {'lastReminderSent': None},
                        {'lastReminderSent': {
                            '$lt': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}}
                    ]
                }
            },
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'userId',
                    'foreignField': '_id',
                    'as': 'user'
                }
            },
            {'$unwind': '$user'}
        ]
        return list(self.db.habits.aggregate(pipeline))