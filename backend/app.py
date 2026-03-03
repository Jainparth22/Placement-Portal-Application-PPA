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

        db.create_all()

        # Create admin user if not exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                email=app.config['ADMIN_EMAIL'],
                password_hash=generate_password_hash(app.config['ADMIN_PASSWORD']),
                role='admin',
                is_active=True,
            )
            db.session.add(admin)
            db.session.commit()
            print(f"[+] Admin user created: {app.config['ADMIN_EMAIL']}")

    # Auth routes

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid email or password'}), 401

        if not user.is_active:
            return jsonify({'error': 'Account is deactivated. Contact admin.'}), 403

        if user.is_blacklisted:
            return jsonify({'error': 'Account is blacklisted. Contact admin.'}), 403

        user.last_login = datetime.utcnow()
        db.session.commit()

        token = generate_token(user)
        response = {
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict(),
        }

        # Include profile info
        if user.role == 'student' and user.student_profile:
            response['profile'] = user.student_profile.to_dict()
        elif user.role == 'company' and user.company_profile:
            response['profile'] = user.company_profile.to_dict()

        return jsonify(response), 200

    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    def logout(user):
        return jsonify({'message': 'Logged out successfully'}), 200

    @app.route('/api/auth/me', methods=['GET'])
    @login_required
    def current_user_info(user):
        response = {'user': user.to_dict()}
        if user.role == 'student' and user.student_profile:
            response['profile'] = user.student_profile.to_dict()
        elif user.role == 'company' and user.company_profile:
            response['profile'] = user.company_profile.to_dict()
        return jsonify(response), 200

    # notifications and jobs

    @app.route('/api/notifications', methods=['GET'])
    @login_required
    def get_notifications(user):
        notifications = Notification.query.filter_by(user_id=user.id).order_by(
            Notification.created_at.desc()
        ).limit(50).all()
        return jsonify([n.to_dict() for n in notifications]), 200

    @app.route('/api/notifications/<int:id>/read', methods=['PUT'])
    @login_required
    def mark_notification_read(user, id):
        notification = Notification.query.get_or_404(id)
        if notification.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        notification.is_read = True
        db.session.commit()
        return jsonify({'message': 'Notification marked as read'}), 200

    @app.route('/api/notifications/read-all', methods=['PUT'])
    @login_required
    def mark_all_read(user):
        Notification.query.filter_by(user_id=user.id, is_read=False).update({'is_read': True})
        db.session.commit()
        return jsonify({'message': 'All notifications marked as read'}), 200

    @app.route('/api/jobs/<int:job_id>', methods=['GET'])
    @login_required
    def get_job_status(user, job_id):
        job = AsyncJob.query.get_or_404(job_id)
        if job.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        return jsonify(job.to_dict()), 200

    # serve frontend

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('index.html')

    return app


