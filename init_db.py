from app import create_app
from app.extensions import db
from app.models import User, Role, Announcement
from werkzeug.security import generate_password_hash

app = create_app()

def get_or_create_role(name, description):
    role = Role.query.filter_by(name=name).first()
    if not role:
        role = Role(name=name, description=description)
        db.session.add(role)
        db.session.flush()
    return role

with app.app_context():
    db.create_all()

    admin_role = get_or_create_role("Super Admin", "Full system administration access.")
    medical_role = get_or_create_role("Medical Expert", "Manage student health records and requests.")
    student_role = get_or_create_role("Student", "Access personal profile, requests and health history.")

    accounts = [
        ("admin@acc.edu", "ACC", "Super Admin", "Admin", "User", "Admin@12345", admin_role),
        ("medical@acc.edu", "ACC", "Medical Expert", "Medical", "Expert", "Medical@12345", medical_role),
        ("student@acc.edu", "ACC", "Student", "Demo", "Student", "Student@12345", student_role),
    ]

    for email, student_id, role_name, first, last, password, role in accounts:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                student_id=None if role_name != "Student" else student_id + "-001",
                first_name=first,
                last_name=last,
                password_hash=generate_password_hash(password),
                is_active=True,
            )
            user.roles.append(role)
            db.session.add(user)
        else:
            if role not in user.roles:
                user.roles.append(role)

    if Announcement.query.count() == 0:
        db.session.add(Announcement(
            title="Welcome to ACC Health Consultation",
            body="Students can submit health requests, review announcements, and access their personal medical history from this portal.",
            is_active=True,
        ))
        db.session.add(Announcement(
            title="Medical Consultation Reminder",
            body="Please provide accurate information when submitting a health request so the Medical Expert can respond appropriately.",
            is_active=True,
        ))

    db.session.commit()
    print("Database initialized successfully.")
    print("Default accounts:")
    print("Super Admin : admin@acc.edu / Admin@12345")
    print("Medical     : medical@acc.edu / Medical@12345")
    print("Student     : student@acc.edu / Student@12345")
