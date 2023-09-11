from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_email(app, message):
    with app.app_context():
        mail.send(message)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    message = Message(subject, sender = app.config['COMMUNICATIONS_EMAIL'], 
            recipients = [to])
    message.body = render_template('email/' + template + '.txt', **kwargs)
    message.html = render_template('email/' + template + '.html', **kwargs)
    
    thread = Thread(target = send_async_email, args = [app, message])
    thread.start()
    return thread
