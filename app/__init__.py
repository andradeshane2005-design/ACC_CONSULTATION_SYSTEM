from pathlib import Path
from flask import Flask
from .extensions import db, login_manager
from .models import User
from .routes.main import main_bp
from .routes.auth import auth_bp
from .routes.admin import admin_bp
from .routes.medical import medical_bp
from .routes.student import student_bp

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.Config")

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(medical_bp, url_prefix="/medical")
    app.register_blueprint(student_bp, url_prefix="/student")

    return app

    @app.errorhandler(403)
    def forbidden(_error):
        from flask import render_template
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(_error):
        from flask import render_template
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        from flask import render_template
        return render_template("500.html"), 500
