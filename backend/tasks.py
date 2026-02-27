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
        now = datetime.datetime.utcnow()
        upcoming_deadline = now + datetime.timedelta(days=3)

        drives = PlacementDrive.query.filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.application_deadline >= now,
            PlacementDrive.application_deadline <= upcoming_deadline
        ).all()

        students = StudentProfile.query.join(User).filter(
            User.is_active == True,
            User.is_blacklisted == False
        ).all()

        count = 0
        for student in students:
            reminder_drives = []
            for drive in drives:
                existing_app = Application.query.filter_by(
                    student_id=student.id, drive_id=drive.id
                ).first()
                if not existing_app:
                    # In-app notification
                    notification = Notification(
                        user_id=student.user_id,
                        message=f"Reminder: Application deadline for '{drive.drive_name}' at {drive.company.company_name} is on {drive.application_deadline.strftime('%Y-%m-%d')}. Apply before it's too late!",
                        channel='email',
                        is_sent=True,
                    )
                    db.session.add(notification)
                    reminder_drives.append(drive)
                    count += 1

            # Send a single email per student with all upcoming drives
            if reminder_drives and student.user and student.user.email:
                drives_html = ''.join([
                    f"<li><strong>{d.drive_name}</strong> at {d.company.company_name} — Deadline: {d.application_deadline.strftime('%Y-%m-%d')}</li>"
                    for d in reminder_drives
                ])
                email_body = f"""
                <html><body>
                <h2>Placement Portal - Upcoming Deadlines</h2>
                <p>Hi {student.full_name},</p>
                <p>The following placement drives have upcoming deadlines (within 3 days):</p>
                <ul>{drives_html}</ul>
                <p>Log in to the Placement Portal to apply before it's too late!</p>
                <p>Best regards,<br>Placement Portal Team</p>
                </body></html>
                """
                send_email(
                    subject="Placement Portal - Upcoming Application Deadlines",
                    recipients=[student.user.email],
                    html_body=email_body
