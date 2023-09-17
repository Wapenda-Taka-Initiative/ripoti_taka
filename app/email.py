import os
import base64
import requests
import flask
from threading import Thread
from email.message import EmailMessage
from flask import current_app, render_template
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from . import create_app

folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../secret')

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = os.path.join(folder, 'credentials.json')
TOKEN_FILE = os.path.join(folder, 'token.json')

os.makedirs(folder, exist_ok = True)

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        print("Greate")
    else:
        print("Not Great")
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
        creds = None
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port = 0)
                gmail_service = build('gmail', 'v1', credentials = creds)
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

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
