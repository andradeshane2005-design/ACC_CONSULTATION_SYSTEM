from functools import wraps
from flask import abort, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .extensions import db
from .models import AuditLog

def roles_required(*role_names):
    normalized = {name.lower() for name in role_names}

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not current_user.is_active:
                abort(403)
            if not any(role.name.lower() in normalized for role in current_user.roles):
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator

def log_action(action, entity=None, entity_id=None, details=None):
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details,
    )
    db.session.add(log)
