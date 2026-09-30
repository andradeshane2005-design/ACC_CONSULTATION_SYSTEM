from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from ..models import User
from ..extensions import db
from ..utils import log_action

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        if not user.is_active:
            flash("Your account is currently deactivated. Contact the administrator.", "danger")
            return render_template("auth/login.html")

        login_user(user)
        log_action("LOGIN", "User", user.id, "Successful login")
        db.session.commit()
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html")

@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        log_action("LOGOUT", "User", current_user.id, "User logged out")
        db.session.commit()
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
