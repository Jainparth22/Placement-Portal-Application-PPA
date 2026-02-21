import os
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from config import Config
from models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application, Notification, AsyncJob
from auth import generate_token, get_current_user, login_required
from cache import cache_get, cache_set, cache_delete
from validators import validate_email

mail = Mail()


def create_app():
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'),
                template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'))
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from routes.admin import admin_bp
    from routes.company import company_bp
    from routes.student import student_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    # Init Celery
    try:
        from celery_worker import init_celery
        init_celery(app)
    except Exception as e:
        print(f'[!] Celery init failed: {e} - async tasks wont work')

    # Create tables and admin user
    with app.app_context():
        os.makedirs(os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'resumes'), exist_ok=True)
        os.makedirs('instance', exist_ok=True)
        os.makedirs('exports', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
