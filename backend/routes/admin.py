import os
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, User, CompanyProfile, StudentProfile, PlacementDrive, Application, DriveApproval, MonthlyReport, Notification, AsyncJob
from auth import role_required
from cache import cache_get, cache_set, cache_delete, cache_delete_pattern
import datetime

admin_bp = Blueprint('admin', __name__)
