import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from models import User


def generate_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(
            seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        ),
        'iat': datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token


def decode_token(token):
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    # get user from jwt token in Authorization header
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    payload = decode_token(token)
    if not payload:
        return None
    user = User.query.get(payload['user_id'])
    if user and user.is_active and not user.is_blacklisted:
        return user
    return None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        return f(user, *args, **kwargs)
    return decorated


def role_required(*roles):
    # decorator - checks if user has one of the required roles
