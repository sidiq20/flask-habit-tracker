# app.py
import datetime
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

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.db = Database()

    # Register blueprints
    app.register_blueprint(pages)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(habits, url_prefix="/habits")

    @app.context_processor
    def inject_date_helpers():
        from datetime import datetime, timedelta
        def date_range(selected_date, days=7):
            # This returns a list of datetime objects from 3 days before to 3 days after selected_date.
            return [selected_date + timedelta(days=i - 3) for i in range(days)]

        default_date = datetime.utcnow()  # using UTC
        return dict(
            date_range=date_range,
            timedelta=timedelta,
            selected_date=default_date,
            datetime=datetime
        )

    # Set up reminder scheduler (unchanged)
    scheduler = BackgroundScheduler()
    reminder_service = ReminderService()
    scheduler.add_job(
        reminder_service.process_reminders,
        'interval',
        hours=1,
        next_run_time=datetime.datetime.now()
    )
    scheduler.start()

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print(app.url_map)
    app.run(debug=True, use_reloader=False, port=3000)
