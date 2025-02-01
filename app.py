import datetime
import wraps
from flask import Flask, session, redirect, url_for, flash, request
from routes.pages import pages
from routes.habits import habits  # Our blueprint defined above is named "habits"
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

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first', 'error')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function

    def prevent_future_completion(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            date_str = request.form.get('date')
            if date_str:
                try:
                    completion_date = datetime.datetime.fromisoformat(date_str)
                    if completion_date.date() > datetime.datetime.now().date():
                        flash("You can't complete habits for future dates", 'error')
                        return redirect(url_for('habits.index'))
                except ValueError:
                    flash('Invalid date format', 'error')
                    return redirect(url_for('habits.index'))
            return f(*args, **kwargs)
        return decorated_function

    app.login_required = login_required
    app.prevent_future_completion = prevent_future_completion

    # Register blueprints
    app.register_blueprint(pages)  # For any extra pages (if you use them)
    from routes.auth import auth
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(habits, url_prefix="/habits")

    # Set up reminder scheduler (if using)
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
    app.run(debug=True, port=3000)
