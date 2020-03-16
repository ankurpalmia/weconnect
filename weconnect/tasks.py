import json

from celery import task
from django.core.mail import send_mail
from django.template.loader import render_to_string

from . import settings
from weconnect.constants import VERIFY_EMAIL_SUBJECT


def send_verify_email(email, token):
    msg_html = render_to_string('templates/verify_email_template.html', {'token': token, 'url': settings.URL})
    msg = ""
    email_subject = VERIFY_EMAIL_SUBJECT
    send_mail(
        email_subject,
        msg,
        settings.EMAIL_HOST_USER,
        [email],
        html_message=msg_html
    )

# This is the decorator which a celery worker uses   
@task()
def send_verify_email_task(email, token):
    return send_verify_email(email, token)
