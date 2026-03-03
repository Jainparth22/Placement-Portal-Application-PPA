import os
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, User, CompanyProfile, StudentProfile, PlacementDrive, Application, DriveApproval, MonthlyReport, Notification, AsyncJob
from auth import role_required
from cache import cache_get, cache_set, cache_delete, cache_delete_pattern
import datetime

admin_bp = Blueprint('admin', __name__)


# admin dashboard (cached)
@admin_bp.route('/api/admin/dashboard', methods=['GET'])
@role_required('admin')
def admin_dashboard(user):
    cached = cache_get('admin_stats')
    if cached:
        return jsonify(cached), 200

    stats = {
        'total_students': StudentProfile.query.count(),
        'total_companies': CompanyProfile.query.count(),
        'total_drives': PlacementDrive.query.count(),
        'pending_companies': CompanyProfile.query.filter_by(approval_status='pending').count(),
        'approved_companies': CompanyProfile.query.filter_by(approval_status='approved').count(),
        'pending_drives': PlacementDrive.query.filter_by(status='pending').count(),
        'approved_drives': PlacementDrive.query.filter_by(status='approved').count(),
        'total_applications': Application.query.count(),
        'selected_students': Application.query.filter_by(status='selected').count(),
        'active_students': User.query.filter_by(role='student', is_active=True).count(),
        'blacklisted_users': User.query.filter_by(is_blacklisted=True).count(),
        # Chart data: application status breakdown
        'chart_app_status': {
            'applied': Application.query.filter_by(status='applied').count(),
            'shortlisted': Application.query.filter_by(status='shortlisted').count(),
            'selected': Application.query.filter_by(status='selected').count(),
            'rejected': Application.query.filter_by(status='rejected').count(),
            'withdrawn': Application.query.filter_by(status='withdrawn').count(),
        },
        # Chart data: drives by status
        'chart_drive_status': {
            'pending': PlacementDrive.query.filter_by(status='pending').count(),
            'approved': PlacementDrive.query.filter_by(status='approved').count(),
            'rejected': PlacementDrive.query.filter_by(status='rejected').count(),
            'closed': PlacementDrive.query.filter_by(status='closed').count(),
        },
    }
    cache_set('admin_stats', stats, ttl=300)
    return jsonify(stats), 200


# search
@admin_bp.route('/api/admin/search', methods=['GET'])
@role_required('admin')
def admin_search(user):
    q = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # all, students, companies
