from flask import Blueprint, request, redirect, url_for, render_template, flash, session, current_app
from datetime import datetime, timedelta
from bson.objectid import ObjectId

pages = Blueprint(
    "habits", __name__, template_folder="templates", static_folder="static"
)

def today_at_midnight():
    today = datetime.today()
    return datetime.combine(today.date(), datetime.min.time())

@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime):
        dates = [start + timedelta(days=diff) for diff in range(-3, 4)]
        return dates
    return {"date_range": date_range}

@pages.route("/")
def index():
    try:
        date_str = request.args.get("date")
        if date_str:
            selected_date = datetime.fromisoformat(date_str)
        else:
            selected_date = today_at_midnight()

        # Get habits for the current user
        habits = current_app.db.get_user_habits(session['user_id'])

        # Get completions for the selected date
        completions = []
        for habit in habits:
            completion = current_app.db.get_completion(str(habit['_id']), selected_date)
            if completion:
                completions.append(str(habit['_id']))

        return render_template(
            "index.html",
            habits=habits,
            selected_date=selected_date,
            completions=completions,
            title="Habit Tracker - Home",
        )
    except ValueError as e:
        flash(f"Invalid date format: {str(e)}", "error")
        return redirect(url_for("habits.index"))
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "error")
        return redirect(url_for("habits.index"))

@pages.route("/complete", methods=["POST"])
def complete():
    try:
        date_string = request.form.get("date")
        if not date_string:
            flash("Date is required", "error")
            return redirect(url_for("habits.index"))

        date = datetime.fromisoformat(date_string)
        habit_id = request.form.get("habitId")
        if not habit_id:
            flash("Habit ID is required", "error")
            return redirect(url_for("habits.index"))

        if current_app.db.complete_habit(habit_id, date):
            flash("Habit marked as complete!", "success")
        else:
            flash("Failed to complete habit", "error")

        return redirect(url_for("habits.index", date=date_string))
    except ValueError as e:
        flash(f"Invalid date format: {str(e)}", "error")
        return redirect(url_for("habits.index"))
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "error")
        return redirect(url_for("habits.index"))