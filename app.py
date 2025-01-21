from flask import Flask, render_template


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("layout.html", title="Habit Tracker - Home")

@app.route("/add", methods=["GET", "POST"])
def add_habit():
    return render_template("add_habit.html", title="Habit Tracker - Home")


if __name__ == "__main__":
    app.run(debug=True, port=3000)