import json

from celery import task
from django.core.mail import send_mail
from django.template.loader import render_to_string

from weconnect import settings
from weconnect.constants import VERIFY_EMAIL_SUBJECT, REQUEST_MAIL_SUBJECT, FORGOT_PASSWORD_MAIL_SUBJECT, URL


def send_verify_email(email, token):
    msg_html = render_to_string('templates/verify_email_template.html', {'token': token, 'url': URL})
    msg = "Please verify your email to access all features of WeConnect Link: {}verify/{}".format(URL, token)
    email_subject = VERIFY_EMAIL_SUBJECT
    send_mail(
        email_subject,
        msg,
        settings.EMAIL_HOST_USER,
        [email],
        html_message=msg_html
    )

def send_friend_request(email, sender, sender_pk, receiver_pk):
    msg_html = render_to_string('templates/friend_request_mail.html', {'sender': sender, 'sender_pk': sender_pk, 'receiver_pk': receiver_pk, 'url': URL})
    msg = "You got a friend request from {sender}. Accept: {url}respond/accept/{sender_pk}/{receiver_pk}, Reject: {url}respond/reject/{sender_pk}/{receiver_pk}".format(sender=sender, url=URL, sender_pk=sender_pk, receiver_pk=receiver_pk)
    email_subject = REQUEST_MAIL_SUBJECT
    send_mail(
        email_subject,
        msg,
        settings.EMAIL_HOST_USER,
        [email],
        html_message=msg_html
    )

def forgot_password_mail(email, token):
    msg_html = render_to_string('templates/forgot_password_mail.html', {'token': token, 'url': URL})
    msg = "You have requested to change your password. Here's the link: {}reset-password/{}".format(URL, token)
    email_subject = FORGOT_PASSWORD_MAIL_SUBJECT
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

@task()
def send_friend_request_task(email, sender, sender_pk, receiver_pk):
    return send_friend_request(email, sender, sender_pk, receiver_pk)

@task()
def forgot_password_mail_task(email, token):
    return forgot_password_mail(email, token)
