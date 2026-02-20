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
