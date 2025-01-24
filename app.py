from flask import Flask
from routes import pages

app = Flask(__name__)
habits = ["Test habit", "Test habit 2"]


@app.context_processor
def add_calc_date_range():
    def date_range(start: datetime.date):
        dates = [start + datetime.timedelta(days=diff) for diff in range (-3, 4)]
        return dates

    return {"date_range": date_range}

@app.route("/")
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.date.fromisoformat(date_str)
    else:
        selected_date = datetime.date.today()

    return render_template(
        "index.html",
        habits=habits,
        title="Habit Tracker - Home",
        selected_date=selected_date,
    )

@app.route("/add", methods=["GET", "POST"])
def add_habit():
    if request.method == "POST":
        habits.append(request.form.get("habit"))
    return render_template("add_habit.html",
                           title="Habit Tracker - Add Habit",
                           selected_date=datetime.date.today(),)


if __name__ == "__main__":
    app.run(debug=True, port=3000)