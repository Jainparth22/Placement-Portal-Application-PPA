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
    admin = User.query.filter_by(role='admin').first()
    if admin:
        notification = Notification(
            user_id=admin.id,
            message=f'New company "{company_name}" registered and awaiting approval.',
            channel='in-app', is_sent=True,
        )
        db.session.add(notification)

    db.session.commit()
    cache_delete('admin_stats')
    return jsonify({'message': 'Company registered successfully. Awaiting admin approval.', 'company': company.to_dict()}), 201


# company profile
@company_bp.route('/api/companies/profile', methods=['GET'])
@role_required('company')
def get_company_profile(user):
    company = CompanyProfile.query.filter_by(user_id=user.id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404
    return jsonify(company.to_dict()), 200


@company_bp.route('/api/companies/profile', methods=['PUT'])
@role_required('company')
def update_company_profile(user):
    company = CompanyProfile.query.filter_by(user_id=user.id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    data = request.json
    if data.get('company_name'):
        ok, err = validate_name(data['company_name'], 'Company name')
        if not ok:
            return jsonify({'error': err}), 400
        company.company_name = data['company_name']
    if data.get('hr_name'):
        company.hr_name = data['hr_name']
    if data.get('hr_email'):
        if not validate_email(data['hr_email']):
            return jsonify({'error': 'HR email is not valid'}), 400
        company.hr_email = data['hr_email']
    if data.get('hr_phone'):
        ok, err = validate_phone(data['hr_phone'])
        if not ok:
            return jsonify({'error': err}), 400
        company.hr_phone = data['hr_phone']
    if data.get('website'):
        ok, err = validate_url(data['website'])
        if not ok:
            return jsonify({'error': err}), 400
        company.website = data['website']
    if data.get('description'):
        company.description = data['description']
    if data.get('industry'):
        company.industry = data['industry']
    if data.get('company_size'):
        company.company_size = data['company_size']

    db.session.commit()
    return jsonify({'message': 'Profile updated', 'company': company.to_dict()}), 200


# company dashboard
@company_bp.route('/api/company/dashboard', methods=['GET'])
@role_required('company')
def company_dashboard(user):
    company = CompanyProfile.query.filter_by(user_id=user.id).first()
    if not company:
        return jsonify({'error': 'Company not found'}), 404

    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    total_applicants = sum(d.applications.count() for d in drives)

    return jsonify({
        'company': company.to_dict(),
        'total_drives': len(drives),
        'total_applicants': total_applicants,
        'drives_summary': [
            {
                'id': d.id,
                'drive_name': d.drive_name,
                'status': d.status,
                'applicants': d.applications.count(),
            }
            for d in drives
        ],
    }), 200


# placement drives
@company_bp.route('/api/company/drives', methods=['GET'])
@role_required('company')
def list_company_drives(user):
    company = CompanyProfile.query.filter_by(user_id=user.id).first()
    if not company:
        return jsonify({'error': 'Company not found'}), 404
    drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(PlacementDrive.id.desc()).all()
    return jsonify([d.to_dict() for d in drives]), 200


@company_bp.route('/api/company/drives', methods=['POST'])
@role_required('company')
def create_drive(user):
    company = CompanyProfile.query.filter_by(user_id=user.id).first()
    if not company:
        return jsonify({'error': 'Company not found'}), 404
    if company.approval_status != 'approved':
        return jsonify({'error': 'Company must be approved by admin before creating drives'}), 403

    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

