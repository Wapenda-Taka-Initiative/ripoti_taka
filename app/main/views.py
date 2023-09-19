import flask
from flask_login import login_user, logout_user, login_required
from . import main
from .. import db
from ..email import send_async_email
from ..models import User

@main.route('/')
@main.route('/home')
@main.route('/homepage')
def index():
    return flask.render_template('main/index.html')


@main.route('/get_involved')
def get_involved():
    return flask.render_template('main/get_involved.html')


@main.route('/contact_us')
def contact_us():
    return flask.render_template('main/contact.html')


@main.route('/terms_and_conditions')
def terms_and_conditions():
    return flask.render_template('main/terms_and_conditions.html')


@main.route('/privacy_policy')
def privacy_policy():
    return flask.render_template('main/privacy_policy.html')


@main.route('/get_gmail_api_authorization_code')
def get_gmail_api_authorization_code():
    provider_data = flask.current_app.config['GMAIL_API_CONFIG']

    # Generate a random string for the state parameter
    flask.session['oauth2_state'] = secrets.token_urlsafe(16)

    # Create a query string with all the OAuth2 parameters
    query_string = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': flask.url_for('main.gmail_api_callback', 
            _external = True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': flask.session['oauth2_state'],
        })
    # Redirect the user to the OAuth2 provider authorization URL
    return flask.redirect(provider_data['authorize_url'] + '?' + query_string)


@main.route('/gmail_api_callback')
def gmail_api_callback():
    provider_data = flask.current_app.config['GMAIL_API_CONFIG']

    # If there was an authentication error, flash the error message and exit
    if 'error' in flask.request.args:
        for key, value in flask.request.args.items():
            if key.startswith('error'):
                flask.flash(f"{key} : {value}")
        return flask.redirect(flask.url_for('main.index'))

    # Ensure the state parameter matches the one created in the authorization
    # request to prevent CSRF
    if flask.request.args['state'] != flask.session.get('oauth2_state'):
        flask.abort(401)

    # Ensure the authorization code is present
    if 'code' not in flask.request.args:
        flask.abort(401)

    # Exchange the authorization code for an access token
    response = requests.post(provider_data['token_url'], 
            data = {
                'client_id' : provider_data['client_id'],
                'client_secret' : provider_data['client_secret'],
                'code' : flask.request.args['code'],
                'redirect_uri' : flask.url_for('main.index', _external = True),
                'scope' : provider_data['scopes'], 
                'access_type' : 'offline'
                }, 
            headers = {"Accept" : "application/json"})

    # Ensure request was a success
    if response.status_code != 200:
        flask.abort(401)

    # Ensure access token was provided
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        flask.abort(401)

    token_file = os.path.join(flask.current_app.config['SECRETS_PATH'],
                'token.json')
    with open(token_file, 'w') as token:
        token.write(response.json())

    send_async_email(flask.session['app'], flask.session['message'])
    return flask.redirect(flask.url_for('profiles.dashboard'))

@main.route('/send_email')
def send_email(to, subject, template, **kwargs):
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
