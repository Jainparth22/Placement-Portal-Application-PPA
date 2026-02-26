import re

# basic input validators

def validate_email(email):
    """check if email looks valid"""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validate_password(password):
    if not password or len(password) < 6:
        return False, 'Password must be at least 6 characters'
    if len(password) > 128:
        return False, 'Password too long'
    return True, None

def validate_phone(phone):
    if not phone:
        return True, None  # phone is optional
    phone = phone.strip()
    # allow digits, spaces, +, -, ()
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    if not cleaned.isdigit():
        return False, 'Phone number should contain only digits'
    if len(cleaned) < 7 or len(cleaned) > 15:
        return False, 'Phone number should be 7-15 digits'
    return True, None

def validate_cgpa(cgpa):
    try:
        val = float(cgpa)
        if val < 0 or val > 10:
            return False, 'CGPA must be between 0 and 10'
        return True, None
    except (ValueError, TypeError):
        return False, 'CGPA must be a number'

def validate_year(year):
    if not year:
        return True, None
    try:
