import os
from celery import Celery

celery = Celery(
    'ppa',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
    include=['tasks']
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    beat_schedule={
        'daily-reminders': {
            'task': 'tasks.send_daily_reminders',
            'schedule': 86400,      # Every 24 hours
        },
        'monthly-report': {
            'task': 'tasks.generate_monthly_report',
            'schedule': 2592000,    # Every 30 days
        },
    },
)


def init_celery(app):
    # set up celery to use flask app context
    celery.conf.update(
        broker_url=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
        result_backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
    )

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# When running as celery worker (not via Flask), create the app context
# This ensures tasks can access db.session, current_app, etc.
try:
    from app import create_app
    _flask_app = create_app()
    init_celery(_flask_app)
except Exception:
