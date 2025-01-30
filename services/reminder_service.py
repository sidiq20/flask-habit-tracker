from datetime import datetime
import pytz
from models.database import Database
from services.email_service import EmailService

class ReminderService:
    def __init__(self):
        self.db = Database()
        self.email_service = EmailService()

    def process_reminders(self):
        """
        Process reminders for all habits that need to be completed
        should be run by a scheduler every hour
        """
        current_hour = datetime.utcnow().strftime('%H:00')
        habits_needing_reminder = self.db.get_habits_needing_reminder(current_hour)

        for habit in habits_needing_reminder:
            user_tz = pytz.timezone(habit['user']['timezone'])
            user_time = datetime.utcnow().astimezone(user_tz)

            if user_time.hour < 19:
                self.email_service.send_reminder(
                    habit['user']['email'],
                    habit['name']
                )

                self.db.habits.update_one(
                    {'_id': habit['_id']},
                    {'$set': {'lastReminderSent': datetime.utcnow()}}
                )