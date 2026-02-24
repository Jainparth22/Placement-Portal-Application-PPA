import csv
import os
import datetime
from celery_worker import celery
from models import db, User, StudentProfile, PlacementDrive, Application, MonthlyReport, Notification, AsyncJob


def send_email(subject, recipients, html_body):
    """Send email via Flask-Mail"""
    try:
        from app import mail
        from flask_mail import Message
        msg = Message(subject=subject, recipients=recipients, html=html_body)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_gchat_webhook(message):
    # send to google chat space
    try:
        import requests
        from flask import current_app
        webhook_url = current_app.config.get('GCHAT_WEBHOOK_URL', '') or os.environ.get('GCHAT_WEBHOOK_URL', '')
        if webhook_url:
            requests.post(webhook_url, json={"text": message}, timeout=10)
            return True
    except Exception as e:
        print(f"Google Chat webhook failed: {e}")
    return False


@celery.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    """Send daily reminders for upcoming deadlines"""
    try:
