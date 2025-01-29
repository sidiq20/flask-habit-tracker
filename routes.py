import datetime
import uuid
from flask import Blueprint, request, redirect, url_for, render_template, current_app, flash
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

pages = Blueprint(
    "habits", __name__, template_folder="templates", static_folder="static"
)


def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)


@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime.datetime):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates

    return {"date_range": date_range}


@pages.route("/")
def index():
    try:
        date_str = request.args.get("date")
        if date_str:
            selected_date = datetime.datetime.fromisoformat(date_str)
        else:
            selected_date = today_at_midnight()

        # Get habits and sort them by name
        habits_on_date = current_app.db.habits.find(
            {"added": {"$lte": selected_date}}
        ).sort("name", 1)

        # Get completions for the selected date
        completions = [
            habit["habit"]
            for habit in current_app.db.completions.find({"date": selected_date})
        ]

        # Get streak information for each habit
        habits_with_streaks = []
        for habit in habits_on_date:
            streak = calculate_streak(habit["_id"], selected_date)
            habit["streak"] = streak
            habits_with_streaks.append(habit)

        return render_template(
            "index.html",
            habits=habits_with_streaks,
            selected_date=selected_date,
            completions=completions,
            title="Habit Tracker - Home",
        )
    except ValueError as e:
        flash(f"Invalid date format: {str(e)}", "error")
        return redirect(url_for(".index"))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for(".index"))


def calculate_streak(habit_id: str, end_date: datetime.datetime) -> int:
    streak = 0
    current_date = end_date

    while True:
        completion = current_app.db.completions.find_one(
            {"habit": habit_id, "date": current_date}
        )
        if not completion:
            break

        streak += 1
        current_date -= datetime.timedelta(days=1)

    return streak


@pages.route("/complete", methods=["POST"])
def complete():
    try:
        date_string = request.form.get("date")
        date = datetime.datetime.fromisoformat(date_string)
        habit_id = request.form.get("habitId")

        # Validate habit exists
        habit = current_app.db.habits.find_one({"_id": habit_id})
        if not habit:
            flash("Habit not found", "error")
            return redirect(url_for(".index", date=date_string))

        try:
            current_app.db.completions.insert_one({"date": date, "habit": habit_id})
            flash("Habit marked as complete!", "success")
        except DuplicateKeyError:
            flash("Habit already completed for this date", "info")

        return redirect(url_for(".index", date=date_string))
    except ValueError:
        flash("Invalid date format", "error")
        return redirect(url_for(".index"))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for(".index"))


@pages.route("/edit/<string:habit_id>", methods=["GET", "POST"])
def edit_habit(habit_id):
    try:
        habit = current_app.db.habits.find_one({"_id": habit_id})
        if not habit:
            flash("Habit not found", "error")
            return redirect(url_for(".index"))

        selected_date = request.args.get("date", today_at_midnight())

        if request.method == "POST":
            new_name = request.form.get("habit")
            if not new_name or not new_name.strip():
                flash("Habit name cannot be empty", "error")
                return render_template(
                    "edit_habit.html",
                    habit=habit,
                    title="Habit Tracker - Edit Habit",
                    selected_date=selected_date,
                )

            current_app.db.habits.update_one(
                {"_id": habit_id},
                {"$set": {"name": new_name.strip()}}
            )
            flash("Habit updated successfully!", "success")
            return redirect(url_for(".index", date=selected_date))

        return render_template(
            "edit_habit.html",
            habit=habit,
            title="Habit Tracker - Edit Habit",
            selected_date=selected_date,
        )
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for(".index"))


@pages.route("/delete/<string:habit_id>", methods=["POST"])
def delete_habit(habit_id):
    try:
        result = current_app.db.habits.delete_one({"_id": habit_id})
        if result.deleted_count:
            current_app.db.completions.delete_many({"habit": habit_id})
            flash("Habit deleted successfully!", "success")
        else:
            flash("Habit not found", "error")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")

    return redirect(url_for(".index"))


@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()

    if request.method == "POST":
        habit_name = request.form.get("habit", "").strip()
        if not habit_name:
            flash("Habit name cannot be empty", "error")
            return render_template(
                "add_habit.html",
                title="Habit Tracker - Add Habit",
                selected_date=today
            )

        try:
            current_app.db.habits.insert_one({
                "_id": uuid.uuid4().hex,
                "added": today,
                "name": habit_name,
            })
            flash("Habit added successfully!", "success")
            return redirect(url_for(".index"))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

    return render_template(
        "add_habit.html",
        title="Habit Tracker - Add Habit",
        selected_date=today
    )


@pages.route("/uncomplete", methods=["POST"])
def uncomplete():
    try:
        date_string = request.form.get("date")
        date = datetime.datetime.fromisoformat(date_string)
        habit_id = request.form.get("habitId")

        result = current_app.db.completions.delete_one({
            "date": date,
            "habit": habit_id
        })

        if result.deleted_count:
            flash("Habit completion removed", "success")
        else:
            flash("Habit completion not found", "info")

        return redirect(url_for(".index", date=date_string))
    except ValueError:
        flash("Invalid date format", "error")
        return redirect(url_for(".index"))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for(".index"))