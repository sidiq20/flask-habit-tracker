import datetime  # Import datetime here
from flask import Flask, session, redirect, url_for, flash, request
from routes.pages import pages
from routes.habits import habits
from routes.auth import auth
from models.database import Database
from services.reminder_service import ReminderService
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os

load_dotenv()
print("MONGO_URI:", os.environ.get("MONGO_URI"))
print("DB_NAME:", os.environ.get("DB_NAME"))
print("SECRET_KEY:", os.environ.get("SECRET_KEY"))
print("SMTP_HOST:", os.environ.get("SMTP_HOST"))
print("SMTP_USER:", os.environ.get("SMTP_USER"))
print("SMTP_PASS:", os.environ.get("SMTP_PASS"))


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    if not os.environ.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY is not set. Please set in the env")
    app.db = Database()

    # Register blueprints
    app.register_blueprint(pages)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(habits, url_prefix="/habits")

    @app.context_processor
    def inject_date_helpers():
        from datetime import datetime, timedelta
        def date_range(selected_date, days=7):
            return [selected_date + timedelta(days=i - 3) for i in range(days)]

        default_date = datetime.utcnow()  # using UTC
        return dict(
            date_range=date_range,
            timedelta=timedelta,
            selected_date=default_date,
            datetime=datetime
        )

    # Set up reminder scheduler
    scheduler = BackgroundScheduler(deamon=True)
    reminder_service = ReminderService()
    scheduler.add_job(
        reminder_service.process_reminders,
        'interval',
        hours=1,
        timezone=datetime.timezone.utc,
        next_run_time=datetime.datetime.now() # Now works since datetime is imported
    )
    scheduler.start()

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print(app.url_map)
    app.run(use_reloader=False, port=3000)
