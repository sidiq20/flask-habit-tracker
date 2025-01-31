from flask import Blueprint, request, redirect, url_for, render_template, flash, session, current_app
from datetime import datetime, timedelta

# Change the blueprint name from 'habits' to 'habits_blueprint'
habits_blueprint = Blueprint("habits_blueprint", __name__)

def date_range(selected_date, days=7):
    """Returns a list of dates for the past 'days' days including 'selected_date'."""
    return [(selected_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)][::-1]


@habits_blueprint.route("/", methods=["GET"])
def index():
    selected_date = datetime.strptime('2025-01-30', '%Y-%m-%d')
    date_range_values = [selected_date + timedelta(days=i) for i in range(7)]  # 7-day range for example

    return render_template('habits/index.html', title="Your Habits", selected_date=selected_date, date_range=date_range_values)

    if not user_id:
        flash("You must be logged in to view your habits.", "error")
        return redirect(url_for("auth.login"))

    habits = current_app.db.get_user_habits(user_id)

    return render_template('habits/index.html',
                           title="Your Habits",
                           selected_date=selected_date,
                           date_range=date_range_values,
                           habits=habits)


@habits_blueprint.route("/add", methods=["GET", "POST"])
def add_habit():
    habit_name = request.form.get("habit_name", "").strip()

    if not habit_name:
        flash("Habit name is required", "error")
        return redirect(url_for("habits_blueprint.index"))

    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to add a habit", "error")
        return redirect(url_for("auth.login"))

        current_app.db.create_habit(user_id, habit_name)
        flash("Habit added successfully!", "success")
        return redirect(url_for("habits_blueprint.index"))
    return render_template("habits/add_habit.html", title="Add habit")


@habits_blueprint.route("/complete", methods=["POST"])
def complete_habit():
    habit_id = request.form.get("habit_id")

    if not habit_id:
        flash("Invalid habit", "error")
        return redirect(url_for("habits_blueprint.index"))

    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to complete a habit", "error")
        return redirect(url_for("auth.login"))

    current_app.db.complete_habit(user_id, habit_id)
    flash("Habit marked as completed!", "success")
    return redirect(url_for("habits_blueprint.index", date=date))

@habits_blueprint.route("/delete/<habit_id>", methods=["POST"])
def delete_habit(habit_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to delete a habit", "error")
        return redirect(url_for("auth.login"))

    habit = current_app.db.get_habit_by_id(habit_id, user_id)
    if not habit:
        flash("Habit not found", "error")
        return redirect(url_for("habits_blueprint.index"))

    current_app.db.delete_habit(habit_id)
    flash("Habit deleted successfully!", "success")
    return redirect(url_for("habits_blueprint.index"))
