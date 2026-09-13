import os

from flask import Flask
from flask_wtf import CSRFProtect

from config import config
from app.extensions import db, login_manager, migrate

csrf = CSRFProtect()


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_CONFIG", "default")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    if config_name == "production" and app.config["SECRET_KEY"] == "dev-key-change-me":
        raise RuntimeError(
            "Refusing to start with the default SECRET_KEY in production. "
            "Set a real SECRET_KEY environment variable (see .env.example)."
        )

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Import models so Flask-Migrate/SQLAlchemy are aware of them
    from app import models  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.recipes import bp as recipes_bp
    app.register_blueprint(recipes_bp, url_prefix="/recipes")

    from app.recommendations import bp as recommendations_bp
    app.register_blueprint(recommendations_bp, url_prefix="/recommendations")

    from app.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix="/users")

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Jinja helper: current year for footer
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {"current_year": datetime.utcnow().year}

    # Basic security headers on every response
    @app.after_request
    def set_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    # Friendly error pages
    from flask import render_template, flash, redirect, url_for
    from flask_wtf.csrf import CSRFError

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(413)
    def too_large(e):
        return render_template("errors/413.html"), 413

    @app.errorhandler(CSRFError)
    def csrf_error(e):
        flash("Your session expired or that form was resubmitted. Please try again.", "warning")
        return redirect(url_for("main.home"))

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app
