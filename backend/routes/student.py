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
    if not ok:
        return jsonify({'error': err}), 400
    ok, err = validate_phone(data.get('phone', ''))
    if not ok:
        return jsonify({'error': err}), 400
    if data.get('cgpa'):
        ok, err = validate_cgpa(data['cgpa'])
        if not ok:
            return jsonify({'error': err}), 400
    if data.get('graduation_year'):
        ok, err = validate_year(data['graduation_year'])
        if not ok:
            return jsonify({'error': err}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role='student',
    )
    db.session.add(user)
    db.session.flush()

    student = StudentProfile(
        user_id=user.id,
        full_name=full_name,
        department=data.get('department', ''),
        cgpa=float(data.get('cgpa', 0)),
        graduation_year=int(data.get('graduation_year', 0)) if data.get('graduation_year') else None,
        phone=data.get('phone', ''),
        bio=data.get('bio', ''),
    )
    db.session.add(student)

    # Add skills
    skills = data.get('skills', [])
    for s in skills:
        skill = Skill(student_id=student.id, skill_name=s.strip())
        db.session.add(skill)

    db.session.commit()
    cache_delete('admin_stats')
    return jsonify({'message': 'Student registered successfully', 'student': student.to_dict()}), 201


# student profile
@student_bp.route('/api/students/profile', methods=['GET'])
@role_required('student')
def get_student_profile(user):
    student = StudentProfile.query.filter_by(user_id=user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    return jsonify(student.to_dict()), 200


@student_bp.route('/api/students/profile', methods=['PUT'])
@role_required('student')
def update_student_profile(user):
    student = StudentProfile.query.filter_by(user_id=user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    data = request.json
    if data.get('full_name'):
        ok, err = validate_name(data['full_name'], 'Full name')
        if not ok:
            return jsonify({'error': err}), 400
        student.full_name = data['full_name']
    if data.get('department'):
        student.department = data['department']
    if 'cgpa' in data:
        ok, err = validate_cgpa(data['cgpa'])
        if not ok:
            return jsonify({'error': err}), 400
        student.cgpa = float(data['cgpa'])
    if data.get('graduation_year'):
        ok, err = validate_year(data['graduation_year'])
        if not ok:
            return jsonify({'error': err}), 400
        student.graduation_year = int(data['graduation_year'])
    if data.get('phone'):
        ok, err = validate_phone(data['phone'])
        if not ok:
            return jsonify({'error': err}), 400
        student.phone = data['phone']
    if data.get('bio'):
        student.bio = data['bio']

    # Update skills
    if 'skills' in data:
        Skill.query.filter_by(student_id=student.id).delete()
        for s in data['skills']:
            skill = Skill(student_id=student.id, skill_name=s.strip())
            db.session.add(skill)

    db.session.commit()
    return jsonify({'message': 'Profile updated', 'student': student.to_dict()}), 200


# upload resume
@student_bp.route('/api/students/upload-resume', methods=['POST'])
@role_required('student')
def upload_resume(user):
    student = StudentProfile.query.filter_by(user_id=user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    if 'resume' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF, DOC, DOCX files allowed'}), 400

    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'resumes')
    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(f"resume_{student.id}_{file.filename}")
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    student.resume_path = filepath
    db.session.commit()
    return jsonify({'message': 'Resume uploaded successfully', 'resume_path': filepath}), 200


# browse drives (cached)
@student_bp.route('/api/student/drives', methods=['GET'])
@role_required('student')
def browse_drives(user):
    search = request.args.get('search', '').strip()
    branch = request.args.get('branch', '').strip()
    min_cgpa = request.args.get('min_cgpa', None, type=float)

    cache_key = f'approved_drives:{search}:{branch}:{min_cgpa}'
    if not search and not branch and min_cgpa is None:
        cached = cache_get('approved_drives')
        if cached:
            return jsonify(cached), 200

    query = PlacementDrive.query.filter_by(status='approved')

    if search:
        query = query.filter(
            (PlacementDrive.drive_name.ilike(f'%{search}%')) |
            (PlacementDrive.job_title.ilike(f'%{search}%')) |
            (PlacementDrive.location.ilike(f'%{search}%'))
        )
    if branch:
        query = query.filter(PlacementDrive.eligibility_branch.ilike(f'%{branch}%'))

    drives = query.order_by(PlacementDrive.application_deadline.asc()).all()
    result = [d.to_dict() for d in drives]

    if not search and not branch and min_cgpa is None:
        cache_set('approved_drives', result, ttl=600)

    return jsonify(result), 200


@student_bp.route('/api/student/drives/<int:id>', methods=['GET'])
@role_required('student')
def drive_detail(user, id):
    drive = PlacementDrive.query.get_or_404(id)
    student = StudentProfile.query.filter_by(user_id=user.id).first()

    result = drive.to_dict()
    # Check if already applied
    if student:
        existing = Application.query.filter_by(student_id=student.id, drive_id=id).first()
        result['already_applied'] = existing is not None
        result['application'] = existing.to_dict() if existing else None
    return jsonify(result), 200


# apply for drive
@student_bp.route('/api/student/apply/<int:drive_id>', methods=['POST'])
@role_required('student')
def apply_for_drive(user, drive_id):
    student = StudentProfile.query.filter_by(user_id=user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != 'approved':
        return jsonify({'error': 'Drive is not currently accepting applications'}), 400

    if drive.application_deadline and drive.application_deadline < datetime.utcnow():
        return jsonify({'error': 'Application deadline has passed'}), 400

    # eligibility
    if drive.min_cgpa and student.cgpa < drive.min_cgpa:
        return jsonify({'error': f'Minimum CGPA requirement is {drive.min_cgpa}. Your CGPA is {student.cgpa}.'}), 400

    if drive.eligible_year and student.graduation_year and student.graduation_year != drive.eligible_year:
        return jsonify({'error': f'This drive is for {drive.eligible_year} graduation year only.'}), 400

    if drive.eligibility_branch and student.department:
        eligible_branches = [b.strip().lower() for b in drive.eligibility_branch.split(',')]
        if eligible_branches and 'all' not in eligible_branches:
            if student.department.lower() not in eligible_branches:
                return jsonify({'error': f'Your department "{student.department}" is not eligible for this drive.'}), 400

    # check if already applied
    existing = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing:
        return jsonify({'error': 'You have already applied for this drive'}), 409

    data = request.json or {}
    application = Application(
        student_id=student.id,
        drive_id=drive_id,
        status='applied',
        cover_letter=data.get('cover_letter', ''),
    )
    db.session.add(application)

    # notify
    notification = Notification(
        user_id=drive.company.user_id,
        message=f'{student.full_name} applied for "{drive.drive_name}".',
        channel='in-app', is_sent=True,
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({'message': 'Application submitted successfully', 'application': application.to_dict()}), 201


# my applications
@student_bp.route('/api/student/applications', methods=['GET'])
@role_required('student')
def my_applications(user):
    student = StudentProfile.query.filter_by(user_id=user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    apps = Application.query.filter_by(student_id=student.id).order_by(Application.application_date.desc()).all()
    return jsonify([a.to_dict() for a in apps]), 200


@student_bp.route('/api/student/applications/<int:id>/withdraw', methods=['PUT'])
@role_required('student')
def withdraw_application(user, id):
    student = StudentProfile.query.filter_by(user_id=user.id).first()
    app = Application.query.get_or_404(id)

    if app.student_id != student.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if app.status in ('selected', 'rejected'):
        return jsonify({'error': 'Cannot withdraw a finalized application'}), 400

    app.status = 'withdrawn'
    db.session.commit()
    return jsonify({'message': 'Application withdrawn', 'application': app.to_dict()}), 200


# placement history
