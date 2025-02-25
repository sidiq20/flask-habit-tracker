from datetime import datetime
import pytz
from models.database import Database
from services.email_service import EmailService

class ReminderService:
    def process_reminders(self):
        current_hour = datetime.utcnow().strftime('%H:00')
        print(f"⏳ Checking reminders for {current_hour}")

        habits_needing_reminder = self.db.get_habits_needing_reminder(current_hour)
        print(f"🔍 Found {len(habits_needing_reminder)} habits needing reminders")

        for habit in habits_needing_reminder:
            print(f"📩 Sending reminder for habit: {habit['name']}")

            user_tz = pytz.timezone(habit['user']['timezone'])
            user_time = datetime.utcnow().astimezone(user_tz)

            if user_time.hour < 19:
                print(f"✅ Sending email to {habit['user']['email']}")
                email_body = f"""
                <h2>Time to complete your habit!</h2>
                <p>Hi there,</p>
                <p>This is a friendly reminder to complete your habit: <strong>{habit['name']}</strong></p>
                <p>Maintaining consistency is key to building good habits. Take a moment to complete it now!</p>
                <p>Best regards,<br>Your Habit Tracker</p>
                """

                success = self.email_service.send_email(habit['user']['email'], "Don't forget your daily habit!",
                                                        email_body)

                if success:
                    print("📌 Marking reminder as sent...")
                    self.db.habits.update_one(
                        {'_id': habit['_id']},
                        {'$set': {'lastReminderSent': datetime.utcnow()}}
                    )
                else:
                    print("❌ Email failed to send.")
