from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from models import db, User, StudentProfile, PlacementDrive, Application, Notification, AsyncJob, Skill, PlacementHistory
from auth import login_required, role_required
from cache import cache_get, cache_set, cache_delete
from datetime import datetime
import os
from validators import validate_email, validate_password, validate_phone, validate_cgpa, validate_year, validate_name

student_bp = Blueprint('student', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# register student
@student_bp.route('/api/students/register', methods=['POST'])
def register_student():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    full_name = data.get('full_name', '').strip()

    if not all([email, password, full_name]):
        return jsonify({'error': 'Email, password, and full name are required'}), 400

    # validate inputs
    if not validate_email(email):
        return jsonify({'error': 'Please enter a valid email address'}), 400
    ok, err = validate_password(password)
    if not ok:
        return jsonify({'error': err}), 400
    ok, err = validate_name(full_name, 'Full name')
