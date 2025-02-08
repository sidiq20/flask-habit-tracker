from flask import Blueprint, request, redirect, url_for, render_template, flash, session, current_app
from datetime import datetime, timedelta
from bson import ObjectId

habits = Blueprint("habits", __name__)

def date_range(selected_date, days=7):
    return [selected_date + timedelta(days=i - 3) for i in range(days)]

@habits.context_processor
def inject_helpers():
    return dict(date_range=date_range, timedelta=timedelta)


@habits.route("/")
def index():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to view habits", "error")
        return redirect(url_for("auth.login"))
    try:
        date_str = request.args.get("date", datetime.utcnow().strftime("%Y-%m-%d"))
        selected_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        flash("Invalid date format", "error")
        return redirect(url_for("habits.index"))

    habits_list = current_app.db.get_user_habits(user_id)
    completions = current_app.db.get_habit_completions(user_id)

    completion_dates = {(str(comp['habitId']), comp['date']) for comp in completions}

    return render_template(
        'habits/index.html',
        habits=habits_list,
        selected_date=selected_date,
        completion_dates=completion_dates,
        today=datetime.utcnow().strftime("%Y-%m-%d")
    )


@habits.route("/add", methods=["GET", "POST"])
def add_habit():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        habit_name = request.form.get("habit_name", "").strip()
        if not habit_name:
            flash("Habit name cannot be empty", "error")
            return redirect(url_for("habits.index"))
        if current_app.db.create_habit(user_id, habit_name):
            flash("Habit added successfully", "success")
        else:
            flash("Failed to create habit", "error")
        return redirect(url_for("habits.index"))
    # For GET, pass the current UTC date as the selected_date (as a string)
    return render_template("habits/add_habit.html", title="Add habit", selected_date=datetime.utcnow())

@habits.route("/complete", methods=["POST"])
def complete_habit():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    habit_id = request.form.get("habit_id")
    date_str = request.form.get("date")
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        flash("Invalid date format", "error")
        return redirect(url_for("habits.index"))
    if current_app.db.complete_habit(user_id, habit_id, date):
        flash("Habit completed!", "success")
    else:
        flash("Failed to complete habit", "error")
    return redirect(url_for("habits.index", date=date_str))

@habits.route("/uncomplete", methods=["POST"])
def uncomplete():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    habit_id = request.form.get("habit_id")
    date_str = request.form.get("date")
    if current_app.db.uncomplete_habit(user_id, habit_id, date_str):
        flash("Completion removed", "success")
    else:
        flash("Failed to remove completion", "error")
    return redirect(url_for("habits.index", date=date_str))

@habits.route("/delete/<habit_id>", methods=["POST"])
def delete_habit(habit_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    if current_app.db.delete_habit(habit_id, user_id):
        flash("Habit deleted", "success")
    else:
        flash("Failed to delete habit", "error")
    return redirect(url_for("habits.index"))

@habits.route("/edit/<habit_id>", methods=["GET", "POST"])
def edit_habit(habit_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    habit = current_app.db.get_habit_by_id(habit_id, user_id)
    if not habit:
        flash("Habit not found", "error")
        return redirect(url_for("habits.index"))
    if request.method == "POST":
        new_name = request.form.get("habit_name", "").strip()
        if not new_name:
            flash("Habit name cannot be empty", "error")
            return redirect(url_for("habits.edit_habit", habit_id=habit_id))
        if current_app.db.update_habit_name(habit_id, new_name):
            flash("Habit updated", "success")
            return redirect(url_for("habits.index"))
        else:
            flash("Failed to update habit", "error")
    return render_template("habits/edit_habit.html", habit=habit)
