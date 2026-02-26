import os
from dotenv import load_dotenv

# Load .env file from the project root (one level up from backend/)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))


class Config:
    # ── Core ──────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'ppa.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── JWT (PyJWT — custom implementation for full control) ──────
    # Note: Flask-Security was evaluated but a custom JWT implementation was
    # chosen to have granular control over token payload, role-based decorators,
    # and blacklist logic. See auth.py for implementation details.
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'change-me-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour in seconds

    # ── Redis ─────────────────────────────────────────────────────
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # ── Celery ────────────────────────────────────────────────────
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

    # ── Mail ──────────────────────────────────────────────────────
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', '')

    # ── Google Chat Webhook (optional) ───────────────────────────
    GCHAT_WEBHOOK_URL = os.environ.get('GCHAT_WEBHOOK_URL', '')

    # ── File Uploads ──────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    # ── Admin (auto-created on first run) ─────────────────────────
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@placementportal.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
