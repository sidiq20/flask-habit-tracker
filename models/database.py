from datetime import datetime, timedelta
from typing import Optional, List
from pymongo import MongoClient
from bson import ObjectId
import os
from werkzeug.security import generate_password_hash, check_password_hash


class Database:
    def __init__(self):
        self.client = MongoClient(os.environ.get('MONGO_URI'))
        self.db = self.client[os.environ.get('DB_NAME', 'habit_tracker')]
        # Initialize default templates if they don't exist
        self._initialize_templates()

    def _initialize_templates(self):
        # Check if templates exist
        if self.db.habits.count_documents({'template': True}) == 0:
            default_templates = [
                {
                    'name': 'Daily Exercise',
                    'category': 'Health',
                    'description': 'Stay active with a 30-minute workout routine',
                    'template': True,
                    'createdAt': datetime.utcnow(),
                    'icon': '🏃‍♂️',
                    'difficulty': 'Intermediate'
                },
                {
                    'name': 'Read a Book',
                    'category': 'Learning',
                    'description': 'Expand your knowledge with 20 minutes of reading',
                    'template': True,
                    'createdAt': datetime.utcnow(),
                    'icon': '📚',
                    'difficulty': 'Beginner'
                },
                {
                    'name': 'Meditate',
                    'category': 'Mindfulness',
                    'description': 'Find inner peace with 10 minutes of meditation',
                    'template': True,
                    'createdAt': datetime.utcnow(),
                    'icon': '🧘‍♂️',
                    'difficulty': 'Beginner'
                },
                {
                    'name': 'Drink Water',
                    'category': 'Health',
                    'description': 'Stay hydrated with 8 glasses of water daily',
                    'template': True,
                    'createdAt': datetime.utcnow(),
                    'icon': '💧',
                    'difficulty': 'Beginner'
                },
                {
                    'name': 'Journal',
                    'category': 'Personal Growth',
                    'description': 'Reflect on your day with 10 minutes of journaling',
                    'template': True,
                    'createdAt': datetime.utcnow(),
                    'icon': '✍️',
                    'difficulty': 'Beginner'
                },
                {
                    'name': 'Learn a Language',
                    'category': 'Learning',
                    'description': 'Practice a new language for 15 minutes',
                    'template': True,
                    'createdAt': datetime.utcnow(),
                    'icon': '🗣️',
                    'difficulty': 'Intermediate'
                },
                {
                    'name': 'Healthy Meal Prep',
                    'category': 'Health',
                    'description': 'Prepare nutritious meals for the day',
                    'template': True,
                    'createdAt': datetime.utcnow(),
                    'icon': '🥗',
                    'difficulty': 'Intermediate'
                },
                {
                    'name': 'Practice Gratitude',
                    'category': 'Mindfulness',
                    'description': 'Write down 3 things you are grateful for',
                    'template': True,
                    'createdAt': datetime.utcnow(),
                    'icon': '🙏',
                    'difficulty': 'Beginner'
                },
                {
                    'name': 'Digital Detox',
                    'category': 'Wellness',
                    'description': 'Take a 1-hour break from screens',
                    'template': True,
                    'createdAt': datetime.utcnow(),
                    'icon': '📵',
                    'difficulty': 'Advanced'
                },
                {
                    'name': 'Morning Routine',
                    'category': 'Productivity',
                    'description': 'Start your day with a structured morning routine',
                    'template': True,
                    'createdAt': datetime.utcnow(),
                    'icon': '🌅',
                    'difficulty': 'Intermediate'
                },
                {
                    'name': 'Practice an Instrument',
                    'category': 'Learning',
                    'description': 'Dedicate 30 minutes to musical practice',
                    'template': True,
                    'createdAt': datetime.utcnow(),
                    'icon': '🎸',
                    'difficulty': 'Advanced'
                },
                {
                    'name': 'Declutter Space',
                    'category': 'Productivity',
                    'description': 'Spend 15 minutes organizing your space',
                    'template': True,
                    'createdAt': datetime.utcnow(),
                    'icon': '🧹',
                    'difficulty': 'Beginner'
                }
            ]
            self.db.habits.insert_many(default_templates)

    def create_user(self, email: str, password: str, timezone: str = 'UTC') -> Optional[dict]:
        try:
            user = {
                'email': email.lower(),
                'password': generate_password_hash(password),
                'timezone': timezone,
                'createdAt': datetime.utcnow(),
                'achievements': [],
                'streak_protection': 1,  # Number of streak protections available
                'total_completions': 0,
                'level': 1,
                'xp': 0
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

    def create_habit(self, user_id: str, name: str, category: str = None, template: bool = False) -> Optional[dict]:
        try:
            habit = {
                'userId': ObjectId(user_id),
                'name': name.strip(),
                'category': category,
                'createdAt': datetime.utcnow(),
                'streak': 0,
                'total_completions': 0,
                'best_streak': 0,
                'template': template,
                'milestones': [
                    {'count': 7, 'achieved': False, 'name': 'Week Warrior'},
                    {'count': 30, 'achieved': False, 'name': 'Monthly Master'},
                    {'count': 100, 'achieved': False, 'name': 'Century Club'},
                    {'count': 365, 'achieved': False, 'name': 'Year Champion'}
                ],
                'statistics': {
                    'weekly_completion_rate': 0,
                    'monthly_completion_rate': 0,
                    'best_performing_days': [],
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
        print(f"🔍 Searching for habits with reminderTime = {current_hour}")
        habits = list(self.db.habits.find({"reminderTime": current_hour}))

        if not habits:
            print("⚠️ No habits found needing reminders.")

        return habits

    def get_habit_templates(self) -> List[dict]:
        return list(self.db.habits.find({'template': True}))

    def get_habit_statistics(self, habit_id: str) -> dict:
        habit = self.db.habits.find_one({'_id': ObjectId(habit_id)})
        completions = list(self.db.completions.find({'habitId': ObjectId(habit_id)}))

        if not habit:
            return {}

        total_days = (datetime.utcnow() - habit.get('createdAt', datetime.utcnow())).days + 1
        completion_rate = len(completions) / total_days if total_days > 0 else 0

        completion_dates = [c['date'] for c in completions]

        return {
            'completion_rate': completion_rate * 100,
            'total_completions': len(completions),
            'best_streak': habit.get('best_streak', 0),  # ✅ Use .get() to avoid KeyError
            'current_streak': habit.get('streak', 0),  # ✅ Use .get() to avoid KeyError
            'completion_dates': completion_dates,
            'best_performing_days': [],
            'worst_performing_days': [],
            'year': datetime.utcnow().year  # Ensure 'year' exists
        }

    def use_streak_protection(self, user_id: str, habit_id: str, date: str) -> bool:
        try:
            user = self.db.users.find_one({'_id': ObjectId(user_id)})
            if user and user.get('streak_protection', 0) > 0:
                # Add a completion with streak protection flag
                self.db.completions.insert_one({
                    'habitId': ObjectId(habit_id),
                    'userId': ObjectId(user_id),
                    'date': date,
                    'protected': True,
                    'createdAt': datetime.utcnow()
                })
                # Decrease streak protection count
                self.db.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$inc': {'streak_protection': -1}}
                )
                return True
            return False
        except Exception as e:
            print(f"Error using streak protection: {e}")
            return False

    def add_achievement(self, user_id: str, achievement: dict) -> bool:
        try:
            self.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$push': {'achievements': achievement}}
            )
            return True
        except Exception as e:
            print(f"Error adding achievement: {e}")
            return False

    def get_user_achievements(self, user_id: str) -> List[dict]:
        user = self.db.users.find_one({'_id': ObjectId(user_id)})
        return user.get('achievements', []) if user else []

    def get_habit_categories(self, user_id: str) -> List[str]:
        habits = self.db.habits.find({'userId': ObjectId(user_id)})
        categories = set()
        for habit in habits:
            if habit.get('category'):
                categories.add(habit['category'])
        return list(categories)

    def share_habit(self, habit_id: str, shared_with_email: str) -> bool:
        try:
            habit = self.db.habits.find_one({'_id': ObjectId(habit_id)})
            shared_with_user = self.db.users.find_one({'email': shared_with_email.lower()})

            if habit and shared_with_user:
                self.db.shared_habits.insert_one({
                    'habitId': habit['_id'],
                    'sharedByUserId': habit['userId'],
                    'sharedWithUserId': shared_with_user['_id'],
                    'createdAt': datetime.utcnow()
                })
                return True
            return False
        except Exception as e:
            print(f"Error sharing habit: {e}")
            return False