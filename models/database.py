from datetime import datetime, timedelta
from typing import Optional
from pymongo import MongoClient
from bson import ObjectId
import os
from werkzeug.security import generate_password_hash, check_password_hash


class Database:
    def __init__(self):
        self.client = MongoClient(os.environ.get('MONGO_URI'))
        self.db = self.client[os.environ.get('DB_NAME', 'habit_tracker')]

    def create_user(self, email: str, password: str, timezone: str = 'UTC') -> Optional[dict]:
        try:
            user = {
                'email': email.lower(),
                'password': generate_password_hash(password),
                'timezone': timezone,
                'createdAt': datetime.utcnow(),
                'achievements': [],
                'streak_protection': 1,
                'total_completion': 0,
                'level': 1,
                'xp': 0,
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

    def create_habit(self, user_id: str, name: str) -> Optional[dict]:
        try:
            habit = {
                'userId': ObjectId(user_id),
                'name': name.strip(),
                'createdAt': datetime.utcnow(),
                'streak': 0,
                'total_completion': 0,
                'best_streak': 0,
                'template': template,
                'milestone': [
                    {'count': 7, 'achieved': False, 'name': 'Week Warrior'},
                    {'count': 30, 'achieved': False, 'name': 'Monthly Master'},
                    {'count': 100, 'achieved': False, 'name': 'Century Club'},
                    {'count': 300, 'achieved': False, 'name': 'Year Champion'},
                ],
                'statistics': {
                    'weekly_completion_rate': 0,
                    'monthly_completion_rate': 0,
                    'best_performance_days': [],
                    'worst_performing_days': []
                }
            }
            result = self.db.habits.insert_one(habit)
            habit['_id'] = result.inserted_id
            return habit
        except Exception as e:
            print(f"Error creating habit: {e}")
            return None

    def get_user_habits(self, user_id: str) -> list:
        return list(self.db.habits.find({'userId': ObjectId(user_id)}))

    def delete_habit(self, habit_id: str, user_id: str) -> bool:
        try:
            result = self.db.habits.delete_one({
                '_id': ObjectId(habit_id),
                'userId': ObjectId(user_id)
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting habit: {e}")
            return False

    def get_habit_by_id(self, habit_id: str, user_id: str) -> Optional[dict]:
        try:
            return self.db.habits.find_one({
                '_id': ObjectId(habit_id),
                'userId': ObjectId(user_id)
            })
        except Exception as e:
            print(f"Error fetching habit: {e}")
            return None

    def update_habit_name(self, habit_id: str, new_name: str) -> bool:
        try:
            result = self.db.habits.update_one(
                {'_id': ObjectId(habit_id)},
                {'$set': {'name': new_name}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating habit name: {e}")
            return False

    def complete_habit(self, user_id: str, habit_id: str, date: datetime) -> bool:
        try:
            date_str = date.strftime("%Y-%m-%d")
            # Insert or update the completion document (and store the date)
            result = self.db.completions.update_one(
                {
                    'habitId': ObjectId(habit_id),
                    'date': date_str
                },
                {'$setOnInsert': {
                    'userId': ObjectId(user_id),
                    'date': date_str,  # <-- Include the date here!
                    'createdAt': datetime.utcnow()
                }},
                upsert=True
            )

            # Calculate new streak based on all completions for this habit
            completions = list(self.db.completions.find(
                {'habitId': ObjectId(habit_id)}
            ).sort('date', -1))

            streak = 0
            current_date = datetime.utcnow().date()
            for comp in completions:
                # Now comp['date'] should be available
                comp_date = datetime.strptime(comp['date'], "%Y-%m-%d").date()
                if comp_date == current_date - timedelta(days=streak):
                    streak += 1
                else:
                    break

            # Update the habit's streak field
            self.db.habits.update_one(
                {'_id': ObjectId(habit_id)},
                {'$set': {'streak': streak}}
            )

            return True
        except Exception as e:
            print(f"Error completing habit: {e}")
            return False

    def uncomplete_habit(self, user_id: str, habit_id: str, date: str) -> bool:
        try:
            result = self.db.completions.delete_one({
                'habitId': ObjectId(habit_id),
                'date': date,
                'userId': ObjectId(user_id)
            })

            # Recalculate streak after uncompleting
            if result.deleted_count > 0:
                completions = list(self.db.completions.find(
                    {'habitId': ObjectId(habit_id)}
                ).sort('date', -1))

                streak = 0
                current_date = datetime.utcnow().date()
                for comp in completions:
                    comp_date = datetime.strptime(comp['date'], "%Y-%m-%d").date()
                    if comp_date == current_date - timedelta(days=streak):
                        streak += 1
                    else:
                        break

                self.db.habits.update_one(
                    {'_id': ObjectId(habit_id)},
                    {'$set': {'streak': streak}}
                )

            return result.deleted_count > 0
        except Exception as e:
            print(f"Error uncompleting habit: {e}")
            return False

    def get_habit_completions(self, user_id: str) -> list:
        return list(self.db.completions.find({
            'userId': ObjectId(user_id)
        }))

    def get_habits_needing_reminder(self, current_hour):
        return self.db.habits.find({"reminderTime": current_hour})

    def get_habit_templates(self) -> List[dict]:
        return list(self.db.habits.find({'templates': True}))

    def get_habit_statistics(self, habit_id: str) -> dict:
        habit = self.db.habits.find_one({'_id': ObjectId(habit_id)})
        completions = list(self.db.completions.find({'habitId': ObjectId(habit_id)}))

        total_days = (datetime.utcnow() - habit['createAt']).days + 1
        completion_rate = len(completions) / total_days if total_days > 0 else 0

        completion_dates = [c['date'] for c in completions]

        day_stats = {}
        for completion in completions:
            date = datetime.strptime(completion['date'], '%Y-%m-%d')
            day = date.strftime('%A')
            day_stats[day] = day_stats.get(day, 0) + 1

        sorted_days = sorted(day_stats.items(), key=lambda x: x[1], reverse=True)
        best_days = sorted_days[:3] if sorted_days else []
        worst_days = sorted_days[-3:] if sorted_days else []

        return {
            'completion_rate': completion_rate * 100,
            'total_completion': len(completions),
            'best_streak': habit['best_streak'],
            'current_streak': habit['streak'],
            'completion_dates': completion_dates,
            'best_performing_days': best_days,
            'worst_performing_days': worst_days
        }
    def use_streak_protection(self, user_id: str, habit_id: str, date: str) -> bool:
        try:
            user = self.db.users.find_one({'_id': ObjectId(user_id)})
            if user and user.get('streaker_protection', 0) > 0:
                self.db.completions.insert_one({
                    'habitId': ObjectId(habit_id),
                    'userId': ObjectId(user_id),
                    'date': date,
                    'protected': True,
                    'createdAt': datetime.utcnow()
                })

                self.db.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$inc': {'streak_protection': -1}}
                )
                return True
            return False
        except Exception as e:
            print(f"Error using streak protection: {e}")
            return False


















