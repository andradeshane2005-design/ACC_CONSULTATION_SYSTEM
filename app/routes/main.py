from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from ..models import Announcement

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).limit(5).all()
    return render_template("index.html", announcements=announcements)

@main_bp.route("/dashboard")
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    if current_user.has_role("Super Admin"):
        return redirect(url_for("admin.dashboard"))
    if current_user.has_role("Medical Expert"):
        return redirect(url_for("medical.dashboard"))
    return redirect(url_for("student.dashboard"))
