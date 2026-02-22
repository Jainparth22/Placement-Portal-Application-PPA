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

