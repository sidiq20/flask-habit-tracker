from flask import Blueprint, request, redirect, url_for, render_template, flash, session, current_app, jsonify
from datetime import datetime, timedelta
from bson import ObjectId
import json

habits = Blueprint("habits", __name__)

def date_range(selected_date, days=7):
    return [selected_date + timedelta(days=i - 3) for i in range(days)]

@habits.context_processor
def inject_helpers():
    return dict(date_range=date_range, timedelta=timedelta)

@habits.route("/habit_templates", methods=["GET", "POST"])
def habit_templates():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        template_id = request.form.get("template_id")

        if not template_id:
            flash("Invalid template selection.", "error")
            return redirect(url_for("habits.habit_templates"))

        # Get template details
        templates = current_app.db.get_habit_templates()
        template = next((t for t in templates if str(t['_id']) == template_id), None)

        if not template:
            flash("Template not found.", "error")
            return redirect(url_for("habits.habit_templates"))

        # Create new habit from template using the description as the name
        if current_app.db.create_habit(user_id, template["description"], template.get("category")):
            flash("Habit created successfully!", "success")
        else:
            flash("Failed to create habit.", "error")
        return redirect(url_for("habits.index"))

    templates = current_app.db.get_habit_templates()
    return render_template("habits/templates.html", templates=templates)

@habits.route("/statistics/<habit_id>")
def habit_statistics(habit_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    stats = current_app.db.get_habit_statistics(habit_id)
    return render_template("habits/statistics.html", stats=stats)

@habits.route("/categories")
def categories():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    categories = current_app.db.get_habit_categories(user_id)
    return render_template("habits/categories.html", categories=categories)

@habits.route("/share/<habit_id>", methods=["POST"])
def share_habit(habit_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    email = request.form.get("email")
    if current_app.db.share_habit(habit_id, email):
        flash("Habit shared successfully!", "success")
    else:
        flash("Failed to share habit", "error")
    return redirect(url_for("habits.index"))

@habits.route("/protect-streak/<habit_id>", methods=["POST"])
def protect_streak(habit_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    date = request.form.get("date")
    if current_app.db.use_streak_protection(user_id, habit_id, date):
        flash("Streak protected!", "success")
    else:
        flash("No streak protection available", "error")
    return redirect(url_for("habits.index"))

@habits.route("/achievements")
def achievements():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    achievements = current_app.db.get_user_achievements(user_id)
    return render_template("habits/achievements.html", achievements=achievements)

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
    print("completions", completions)

    completion_dates = {(str(comp.get('habitId', '')), comp['date']) for comp in completions if 'habitId' in comp}

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