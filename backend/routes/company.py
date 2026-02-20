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
