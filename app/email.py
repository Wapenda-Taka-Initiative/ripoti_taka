import os
import base64
import requests
import flask
import secrets
from threading import Thread
from email.message import EmailMessage
from flask import current_app, render_template
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from . import create_app

def send_async_email(app, message):
    with app.app_context():
        folder = flask.current_app.config['SECRETS_PATH']
        SCOPES = flask.current_app.config['GMAIL_API_CONFIG'].get('scopes')
        CREDENTIALS_FILE = os.path.join(folder, 'credentials.json')
        TOKEN_FILE = os.path.join(folder, 'token.json')

        creds = None
        if os.path.exists(CREDENTIALS_FILE):
            try:
                creds = credentials.Credentials.from_authorized_user_file(
                    CREDENTIALS_FILE, SCOPES)
            except Exception as e:
                print(f"An error occurred: {e}")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                return flask.redirect('/main/get_gmail_api_authorization_code')

        gmail_service = build('gmail', 'v1', credentials = creds)
        try:
            message = gmail_service.users().messages().send(userId = 'me',
                body = message).execute()
            return message

        except Exception as e:
            raise Exception(f"An error occurred while sending the email: {e}")


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    
    # Build the message object
    message = EmailMessage()
    message['To'] = to
    message['Subject'] = subject
    message.set_content("This is sample email.")
    message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    # Send message asynchronously
    thread = Thread(target = send_async_email, args = [app, message])
    thread.start()
    return thread
