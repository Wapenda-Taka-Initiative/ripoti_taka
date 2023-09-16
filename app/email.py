import os
import base64
import flask
from threading import Thread
from flask import current_app, render_template
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from . import create_app

folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../secrets/')


SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = os.path.join(folder, 'credentials.json')
TOKEN_FILE = os.path.join(folder, 'token.json')

os.makedirs(folder, exist_ok = True)


class Message:
    def __init__(self, recipients, subject, template, **kwargs):
        self.recipients = recipients
        self.subject = subject
        self.template = template
        self.kwargs = kwargs


def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = credentials.Credentials.from_authorized_user_file(
                TOKEN_FILE, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port = 0)
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        return build('gmail', 'v1', credentials = creds)


def send_async_email(app, message):
    with app.app_context():
            gmail_service = get_gmail_service()
            print(gmail_service)
            raw_message = create_raw_message(create_message(message))
            send_message(gmail_service, 'me', raw_message)


def create_message(email_message):
    message = f"Subject: {email_message.subject}\n"
    message += f"To: {email_message.recipients}\n"
    message += f"Content-Type: text/html; charset=utf-8\n\n"
    return message


def create_raw_message(message):
    return {'raw': base64.urlsafe_b64encode(message.encode()).decode()}


def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId = user_id, 
                body = message).execute()
        return message
    except Exception as e:
        raise Exception(f"An error occurred while sending the email: {e}")


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    message = Message(subject = subject, template = template, 
            recipients = to, **kwargs)
    thread = Thread(target = send_async_email, args = [app, message])
    thread.start()
    return thread
