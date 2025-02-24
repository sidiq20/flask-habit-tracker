from flask import Blueprint, render_template, session

pages = Blueprint("pages", __name__)

@pages.route("/")
def index():
    return render_template("hero.html", title="Streaker - Build Better Habits")