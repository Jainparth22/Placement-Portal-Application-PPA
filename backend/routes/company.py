from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, User, CompanyProfile, PlacementDrive, Application, Interview, Notification
from auth import login_required, role_required
from cache import cache_delete, cache_delete_pattern
from datetime import datetime
from validators import validate_email, validate_password, validate_phone, validate_url, validate_cgpa, validate_year, validate_name

company_bp = Blueprint('company', __name__)


# register company
@company_bp.route('/api/companies/register', methods=['POST'])
def register_company():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    company_name = data.get('company_name', '').strip()

    if not all([email, password, company_name]):
        return jsonify({'error': 'Email, password, and company name are required'}), 400

    # validate inputs
    if not validate_email(email):
        return jsonify({'error': 'Please enter a valid email address'}), 400
    ok, err = validate_password(password)
    if not ok:
        return jsonify({'error': err}), 400
    ok, err = validate_name(company_name, 'Company name')
    if not ok:
        return jsonify({'error': err}), 400
    ok, err = validate_phone(data.get('hr_phone', ''))
    if not ok:
        return jsonify({'error': err}), 400
    ok, err = validate_url(data.get('website', ''))
    if not ok:
        return jsonify({'error': err}), 400
    if data.get('hr_email') and not validate_email(data['hr_email']):
        return jsonify({'error': 'HR email is not valid'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role='company',
    )
    db.session.add(user)
    db.session.flush()

    company = CompanyProfile(
        user_id=user.id,
        company_name=company_name,
        hr_name=data.get('hr_name', ''),
        hr_email=data.get('hr_email', email),
        hr_phone=data.get('hr_phone', ''),
        website=data.get('website', ''),
        description=data.get('description', ''),
        industry=data.get('industry', ''),
        company_size=data.get('company_size', ''),
        approval_status='pending',
    )
    db.session.add(company)

    # Notify admin
