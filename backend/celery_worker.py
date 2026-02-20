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
