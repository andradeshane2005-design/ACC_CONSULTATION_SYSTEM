from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from ..models import User, Role, MedicalRecord, HealthRequest, Appointment
from ..extensions import db
from ..utils import roles_required, log_action

medical_bp = Blueprint("medical", __name__)

@medical_bp.route("/")
@roles_required("Medical Expert")
def dashboard():
    stats = {
        "students": User.query.filter(User.roles.any(Role.name == "Student")).count(),
        "records": MedicalRecord.query.count(),
        "pending_requests": HealthRequest.query.filter_by(status="Pending").count(),
        "appointments": Appointment.query.filter_by(status="Requested").count(),
    }
    requests = HealthRequest.query.order_by(HealthRequest.created_at.desc()).limit(8).all()
    return render_template("medical/dashboard.html", stats=stats, requests=requests)

@medical_bp.route("/records")
@roles_required("Medical Expert")
def records():
    records = MedicalRecord.query.order_by(MedicalRecord.updated_at.desc()).all()
    return render_template("medical/records.html", records=records)

@medical_bp.route("/records/new", methods=["GET", "POST"])
@roles_required("Medical Expert")
def create_record():
    students = User.query.filter(User.roles.any(Role.name == "Student"), User.is_active.is_(True)).order_by(User.last_name).all()
    if request.method == "POST":
        record = MedicalRecord(
            student_id=int(request.form["student_id"]),
            blood_type=request.form.get("blood_type"),
            allergies=request.form.get("allergies"),
            medical_conditions=request.form.get("medical_conditions"),
            medications=request.form.get("medications"),
            emergency_contact=request.form.get("emergency_contact"),
            emergency_phone=request.form.get("emergency_phone"),
            notes=request.form.get("notes"),
        )
        db.session.add(record)
        db.session.flush()
        log_action("CREATE", "MedicalRecord", record.id, f"Created medical record for student {record.student_id}")
        db.session.commit()
        flash("Medical record created.", "success")
        return redirect(url_for("medical.records"))
    return render_template("medical/record_form.html", record=None, students=students)

@medical_bp.route("/records/<int:record_id>/edit", methods=["GET", "POST"])
@roles_required("Medical Expert")
def edit_record(record_id):
    record = db.session.get(MedicalRecord, record_id)
    if not record:
        abort(404)
    students = User.query.filter(User.roles.any(Role.name == "Student")).order_by(User.last_name).all()
    if request.method == "POST":
        record.student_id = int(request.form["student_id"])
        record.blood_type = request.form.get("blood_type")
        record.allergies = request.form.get("allergies")
        record.medical_conditions = request.form.get("medical_conditions")
        record.medications = request.form.get("medications")
        record.emergency_contact = request.form.get("emergency_contact")
        record.emergency_phone = request.form.get("emergency_phone")
        record.notes = request.form.get("notes")
        log_action("UPDATE", "MedicalRecord", record.id, "Updated medical record")
        db.session.commit()
        flash("Medical record updated.", "success")
        return redirect(url_for("medical.records"))
    return render_template("medical/record_form.html", record=record, students=students)

@medical_bp.route("/requests")
@roles_required("Medical Expert")
def requests():
    requests = HealthRequest.query.order_by(HealthRequest.created_at.desc()).all()
    return render_template("medical/requests.html", requests=requests)

@medical_bp.post("/requests/<int:request_id>/respond")
@roles_required("Medical Expert")
def respond_request(request_id):
    health_request = db.session.get(HealthRequest, request_id)
    if not health_request:
        abort(404)
    health_request.status = request.form.get("status", "Responded")
    health_request.response = request.form.get("response", "").strip()
    log_action("RESPOND", "HealthRequest", health_request.id, f"Status: {health_request.status}")
    db.session.commit()
    flash("Health request response saved.", "success")
    return redirect(url_for("medical.requests"))

@medical_bp.route("/appointments")
@roles_required("Medical Expert")
def appointments():
    appointments = Appointment.query.order_by(Appointment.appointment_date.asc()).all()
    return render_template("medical/appointments.html", appointments=appointments)

@medical_bp.post("/appointments/<int:appointment_id>/update")
@roles_required("Medical Expert")
def update_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        abort(404)
    appointment.status = request.form.get("status", appointment.status)
    appointment.notes = request.form.get("notes", appointment.notes)
    appointment.medical_expert_id = request.form.get("medical_expert_id") or appointment.medical_expert_id
    log_action("UPDATE", "Appointment", appointment.id, f"Status: {appointment.status}")
    db.session.commit()
    flash("Appointment updated.", "success")
    return redirect(url_for("medical.appointments"))

@medical_bp.route("/reports")
@roles_required("Medical Expert")
def reports():
    total_records = MedicalRecord.query.count()
    total_requests = HealthRequest.query.count()
    pending = HealthRequest.query.filter_by(status="Pending").count()
    responded = HealthRequest.query.filter_by(status="Responded").count()
    appointments = Appointment.query.count()
    return render_template("medical/reports.html",
                           total_records=total_records,
                           total_requests=total_requests,
                           pending=pending,
                           responded=responded,
                           appointments=appointments)
