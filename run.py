"""
run.py — Entry point for the PPA (Placement Portal Application)

Usage:
    python run.py               # Development server (debug mode)
    python run.py --prod        # Production mode (no debug)

For production, prefer gunicorn:
    gunicorn -w 4 -b 0.0.0.0:5001 "backend.app:create_app()"

For Celery worker (separate terminal):
    celery -A backend.celery_worker.celery worker --loglevel=info

For Celery beat scheduler (separate terminal):
    celery -A backend.celery_worker.celery beat --loglevel=info
"""

import sys
import os

# Add backend/ to path so imports resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app

app = create_app()

if __name__ == '__main__':
    prod = '--prod' in sys.argv
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5001)),
        debug=not prod,
    )
