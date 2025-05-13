from flask_mail import Message
from flask import render_template
from . import mail
from flask import current_app
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_booking_confirmation(booking):
    send_email(
        subject='Booking Confirmation',
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[booking.user.email],
        text_body=render_template('email/booking_confirmation.txt', booking=booking),
        html_body=render_template('email/booking_confirmation.html', booking=booking)
    )

def send_booking_notification_to_agent(booking):
    send_email(
        subject='New Property Viewing Request',
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[booking.property.owner.email],
        text_body=render_template('email/booking_notification.txt', booking=booking),
        html_body=render_template('email/booking_notification.html', booking=booking)
    )

def send_payment_confirmation(payment):
    send_email(
        subject='Payment Confirmation',
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[payment.user.email],
        text_body=render_template('email/payment_confirmation.txt', payment=payment),
        html_body=render_template('email/payment_confirmation.html', payment=payment)
    )