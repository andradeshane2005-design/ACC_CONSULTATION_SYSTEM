from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from ..models import MedicalRecord, HealthRequest, Appointment, Announcement
from ..extensions import db
from ..utils import roles_required, log_action

student_bp = Blueprint("student", __name__)

@student_bp.route("/")
@roles_required("Student")
def dashboard():
    requests = HealthRequest.query.filter_by(student_id=current_user.id).order_by(HealthRequest.created_at.desc()).limit(5).all()
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).limit(5).all()
    return render_template("student/dashboard.html", requests=requests, announcements=announcements)

@student_bp.route("/profile", methods=["GET", "POST"])
@roles_required("Student")
def profile():
    if request.method == "POST":
        current_user.first_name = request.form.get("first_name", "").strip()
        current_user.last_name = request.form.get("last_name", "").strip()
        current_user.phone = request.form.get("phone") or None
        current_user.program = request.form.get("program") or None
        current_user.year_level = request.form.get("year_level") or None
        new_password = request.form.get("password", "")
        if new_password:
            current_user.set_password(new_password)
        log_action("UPDATE", "User", current_user.id, "Student updated own profile")
        db.session.commit()
        flash("Profile saved successfully.", "success")
    return render_template("student/profile.html")

@student_bp.route("/requests", methods=["GET", "POST"])
@roles_required("Student")
def requests():
    if request.method == "POST":
        health_request = HealthRequest(
            student_id=current_user.id,
            subject=request.form.get("subject", "").strip(),
            description=request.form.get("description", "").strip(),
            status="Pending",
        )
        db.session.add(health_request)
        db.session.flush()
        log_action("CREATE", "HealthRequest", health_request.id, health_request.subject)
        db.session.commit()
        flash("Health request submitted.", "success")
        return redirect(url_for("student.requests"))
    requests = HealthRequest.query.filter_by(student_id=current_user.id).order_by(HealthRequest.created_at.desc()).all()
    return render_template("student/requests.html", requests=requests)

@student_bp.route("/history")
@roles_required("Student")
def history():
    records = MedicalRecord.query.filter_by(student_id=current_user.id).order_by(MedicalRecord.updated_at.desc()).all()
    return render_template("student/history.html", records=records)

@student_bp.route("/appointments", methods=["GET", "POST"])
@roles_required("Student")
def appointments():
    if request.method == "POST":
        date_text = request.form.get("appointment_date", "")
        try:
            appointment_date = datetime.fromisoformat(date_text)
        except ValueError:
            flash("Please provide a valid appointment date.", "danger")
            return redirect(url_for("student.appointments"))
        appointment = Appointment(
            student_id=current_user.id,
            appointment_date=appointment_date,
            reason=request.form.get("reason", "").strip(),
            status="Requested",
        )
        db.session.add(appointment)
        db.session.flush()
        log_action("CREATE", "Appointment", appointment.id, "Student requested appointment")
        db.session.commit()
        flash("Appointment request submitted.", "success")
        return redirect(url_for("student.appointments"))
    appointments = Appointment.query.filter_by(student_id=current_user.id).order_by(Appointment.appointment_date.desc()).all()
    return render_template("student/appointments.html", appointments=appointments)

@student_bp.route("/announcements")
@roles_required("Student")
def announcements():
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).all()
    return render_template("student/announcements.html", announcements=announcements)
