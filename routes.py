import datetime
import uuid
from flask import Blueprint, request, redirect, url_for, render_template, current_app

pages = Blueprint(
    "habits", __name__, template_folder="templates", static_folder="static"
)


@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime.datetime):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates

    return {"date_range": date_range}


def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)


@pages.route("/")
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()

    habits_on_date = current_app.db.habits.find({"added": {"$lte": selected_date}})
    completions = [
        habit["habit"]
        for habit in current_app.db.completions.find({"date": selected_date})
    ]

    return render_template(
        "index.html",
        habits=habits_on_date,
        selected_date=selected_date,
        completions=completions,
        title="Habit Tracker - Home",
    )


@pages.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    date = datetime.datetime.fromisoformat(date_string)
    habit = request.form.get("habitId")
    current_app.db.completions.insert_one({"date": date, "habit": habit})

    return redirect(url_for(".index", date=date_string))

@pages.route("/edit/<string:habit_id>", methods=["GET", "POST"])
def edit_habit(habit_id):
    habit = current_app.db.habits.find_one({"_id": habit_id})
    selected_date = request.args.get("date", today_at_midnight())

    if request.method == "POST":
        new_name = request.form.get("habit")
        current_app.db.habits.update_one({"_id": habit_id}, {"$set": {"name": new_name}})
        return redirect(url_for(".index", date=selected_date))

    return render_template(
        "edit_habit.html",
        habit=habit,
        title="Habit Tracker - Edit Habit",
        selected_date=selected_date,
    )

@pages.route("/delete/<string:habit_id>", methods=["POST"])
def delete_habit(habit_id):
    current_app.db.habits.delete_one({"_id": habit_id})
    current_app.db.completions.delete_many({"habit": habit_id})
    return redirect(url_for(".index"))


@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()

    if request.form:
        current_app.db.habits.insert_one(
            {"_id": uuid.uuid4().hex, "added": today, "name": request.form.get("habit")}
        )

    return render_template(
        "add_habit.html", title="Habit Tracker - Add Habit", selected_date=today
    )