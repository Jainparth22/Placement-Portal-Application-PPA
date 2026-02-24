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
