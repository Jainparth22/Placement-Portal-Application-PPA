import re

# basic input validators

def validate_email(email):
    """check if email looks valid"""
    if not email or not isinstance(email, str):
        return False
