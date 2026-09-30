from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from sqlalchemy import or_
from ..models import User, Role, Announcement, AuditLog, MedicalRecord, HealthRequest, Appointment
from ..extensions import db
from ..utils import roles_required, log_action

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/")
@roles_required("Super Admin")
def dashboard():
    stats = {
        "users": User.query.count(),
        "students": User.query.filter(User.roles.any(Role.name == "Student")).count(),
        "medical_experts": User.query.filter(User.roles.any(Role.name == "Medical Expert")).count(),
        "requests": HealthRequest.query.count(),
        "records": MedicalRecord.query.count(),
    }
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(8).all()
    return render_template("admin/dashboard.html", stats=stats, logs=logs)

@admin_bp.route("/users")
@roles_required("Super Admin")
def users():
    q = request.args.get("q", "").strip()
    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.first_name.ilike(like), User.last_name.ilike(like), User.email.ilike(like), User.student_id.ilike(like)))
    users = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users, q=q)

@admin_bp.route("/users/new", methods=["GET", "POST"])
@roles_required("Super Admin")
def create_user():
    roles = Role.query.order_by(Role.name).all()
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return render_template("admin/user_form.html", user=None, roles=roles)

        role = db.session.get(Role, int(request.form["role_id"]))
        if not role:
            flash("Invalid role.", "danger")
            return render_template("admin/user_form.html", user=None, roles=roles)

        user = User(
            email=email,
            student_id=request.form.get("student_id") or None,
            first_name=request.form.get("first_name", "").strip(),
            last_name=request.form.get("last_name", "").strip(),
            phone=request.form.get("phone") or None,
            program=request.form.get("program") or None,
            year_level=request.form.get("year_level") or None,
            is_active=True,
        )
        user.set_password(request.form.get("password", ""))
        user.roles.append(role)
        db.session.add(user)
        db.session.flush()
        log_action("CREATE", "User", user.id, f"Created account with role {role.name}")
        db.session.commit()
        flash("User account created successfully.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", user=None, roles=roles)

@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@roles_required("Super Admin")
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    roles = Role.query.order_by(Role.name).all()

    if request.method == "POST":
        user.email = request.form.get("email", "").strip().lower()
        user.student_id = request.form.get("student_id") or None
        user.first_name = request.form.get("first_name", "").strip()
        user.last_name = request.form.get("last_name", "").strip()
        user.phone = request.form.get("phone") or None
        user.program = request.form.get("program") or None
        user.year_level = request.form.get("year_level") or None
        role = db.session.get(Role, int(request.form["role_id"]))
        if role:
            user.roles = [role]
        new_password = request.form.get("password", "")
        if new_password:
            user.set_password(new_password)
        user.is_active = request.form.get("is_active") == "1"
        log_action("UPDATE", "User", user.id, "Updated account")
        db.session.commit()
        flash("User updated successfully.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/user_form.html", user=user, roles=roles)

@admin_bp.post("/users/<int:user_id>/toggle")
@roles_required("Super Admin")
def toggle_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "warning")
        return redirect(url_for("admin.users"))
    user.is_active = not user.is_active
    log_action("DEACTIVATE" if not user.is_active else "ACTIVATE", "User", user.id)
    db.session.commit()
    flash(f"User account {'activated' if user.is_active else 'deactivated'}.", "success")
    return redirect(url_for("admin.users"))

@admin_bp.route("/announcements", methods=["GET", "POST"])
@roles_required("Super Admin")
def announcements():
    if request.method == "POST":
        announcement = Announcement(
            title=request.form.get("title", "").strip(),
            body=request.form.get("body", "").strip(),
            is_active=True,
        )
        db.session.add(announcement)
        db.session.flush()
        log_action("CREATE", "Announcement", announcement.id, announcement.title)
        db.session.commit()
        flash("Announcement published.", "success")
        return redirect(url_for("admin.announcements"))
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template("admin/announcements.html", announcements=announcements)

@admin_bp.post("/announcements/<int:announcement_id>/toggle")
@roles_required("Super Admin")
def toggle_announcement(announcement_id):
    item = db.session.get(Announcement, announcement_id)
    if not item:
        abort(404)
    item.is_active = not item.is_active
    log_action("UPDATE", "Announcement", item.id, "Toggled announcement visibility")
    db.session.commit()
    return redirect(url_for("admin.announcements"))

@admin_bp.route("/logs")
@roles_required("Super Admin")
def logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(250).all()
    return render_template("admin/logs.html", logs=logs)
