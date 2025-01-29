from flask import (request, redirect, url_for, render_template,
                   current_app, flash, session, Blueprint)
from datetime import datetime
from .routes import pages
from .auth import auth
from flask import Blueprint

pages = Blueprint("pages", __name__)

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        timezone = request.form.get("timezone", "UTC")

        if not email or not password:
            flash("Email and password are not required ", "error")
            return redirect(url_for(".register"))

        existing_user = current_app.db.get_user_by_email(email)
        if existing_user:
            flash("Email already registered", "error")
            return redirect(url_for(".register"))

        user = current_app.db.create_user(email, password, timezone)
        if user:
            session["user_id"] = str(user["_id"])
            flash("registration successful", "success")
            return redirect(url_for("habits.index"))
        else:
            flash("Registration failed", "error")

    return render_template("auth/register.html", title="Register")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Not email and password", "error")
            return redirect(url_for(".login"))

        user = current_app.db.get_user_by_email(email)
        if user and current_app.db.verify_password(user, password):
            session["user_id"] = str(user["_id"])
            flash("Login successful!", "success")
            return redirect(url_for("habits.index"))
        else:
            flash("Invalid email or password", "error")

    return render_template("auth/login.html", title="Login")

@auth.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for(".login"))