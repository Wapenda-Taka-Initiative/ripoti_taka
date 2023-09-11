import flask
import os
from flask_login import current_user, login_required
from . import registration
from .forms import (RegistrationForm, EditUserProfileForm, ResetPasswordForm, 
        ResetUsernameForm, ResetEmailForm)
from .utilities import send_password_reset_email
from .. import db
from ..models import User
from ..email import send_email


@registration.route('/edit_profile_image/<int:user_id>', methods = ['GET', 'POST'])
@login_required
def edit_profile_image(user_id):
    user = User.query.get(user_id)
    image_file = flask.request.files.get('profile-image')
    if image_file:
        filename = f"{user_id}.{image_file.filename.split('.')[-1]}"

        # Save file in local storage
        images_path = flask.current_app.config['USER_IMAGES_UPLOAD_PATH']
        os.makedirs(images_path, exist_ok = True)
        image_path = os.path.join(images_path, filename)
        image_file.save(image_path)
        
        # Update user profileUrl in database
        user.imageUrl = filename
        db.session.add(user)
        db.session.commit()
        flask.flash("Profile image updated successfully")

        # Redirect user accordingly
        return flask.redirect(
                flask.url_for('profiles.contributor_profile', user_id=user_id))
    
    # No image found
    flask.flash("Profile image update failed")
    return flask.redirect(
            flask.url_for('profiles.contributor_profile', user_id=user_id))


@registration.route('/register', methods = ['GET', 'POST'])
def register_user():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
                emailAddress = form.email_address.data,
                userName = form.user_name.data,
                password = form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, "Confirm Your Account", 
                "authentication/email/confirm", user = user, token = token)
        flask.flash("A confirmation email has been sent to you.")
        return flask.redirect(flask.url_for('main.index'))

    return flask.render_template('registration/register_user.html', form = form)


@registration.route('/edit_user_profile/<int:user_id>', methods = ['GET', 'POST'])
@login_required
def edit_user_profile(user_id):
    user = User.query.get(user_id)

    form = EditUserProfileForm()
    form.gender.choices = [('Male', 'Male'), ('Female', 'Female')]
    if form.validate_on_submit():
        user.firstName = form.firstName.data
        user.middleName = form.middleName.data
        user.lastName = form.lastName.data
        user.gender = form.gender.data
        user.phoneNumber = form.phoneNumber.data
        user.locationAddress = form.locationAddress.data
        user.about_me = form.about_me.data
        
        db.session.add(user)
        db.session.commit()
        flask.flash("User profile updated successfully")

        if user.userId == current_user.userId:
            return flask.redirect(flask.url_for('profiles.user_profile'))
        else:
            return flask.redirect(
                    flask.url_for('profiles.contributor_profile', user_id=user_id))

    form.firstName.data = user.firstName
    form.middleName.data = user.middleName
    form.lastName.data = user.lastName
    form.phoneNumber.data = user.phoneNumber
    form.gender.data = user.gender
    form.locationAddress.data = user.locationAddress
    form.about_me.data = user.about_me
    
    return flask.render_template('registration/edit_user_profile.html', 
            form = form, user_id = user_id)


# Reset password endpoint functions
@registration.route('/reset_password_request')
@login_required
def reset_password_request():
    send_password_reset_email(user)
    flask.flash("Check your email for the instruction to reset your password")
    return flask.redirect(flask.url_for('authentication.logout'))


@registration.route('/reset_password/<token>', method = ['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_credential_token(token)
    if not user:
        return flask.redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flask.flash('Your password has been reset successfully')
        return flask.redirect(flask.url_for('authentication.login'))

    return flask.render_template('registration/reset_password.html', form = form)


# Reset password endpoint functions
@registration.route('/reset_username_request')
@login_required
def reset_username_request():
    send_username_reset_email(user)
    flask.flash("Check your email for the instruction to reset your username")
    return flask.redirect(flask.url_for('authentication.logout'))


@registration.route('/reset_username/<token>', method = ['GET', 'POST'])
def reset_username(token):
    user = User.verify_reset_credential_token(token)
    if not user:
        return flask.redirect(url_for('main.index'))
    
    form = ResetUsernameForm()
    if form.validate_on_submit():
        user.userName = form.user_name.data
        db.session.commit()
        flask.flash('Your username has been reset successfully')
        return flask.redirect(flask.url_for('authentication.login'))

    return flask.render_template('registration/reset_username.html', form = form)


# Reset email endpoint functions
@registration.route('/reset_email_request')
@login_required
def reset_email_request():
    send_email_reset_email(user)
    flask.flash("Check your email for the instruction to reset your email")
    return flask.redirect(flask.url_for('authentication.logout'))


@registration.route('/reset_email/<token>', method = ['GET', 'POST'])
def reset_email(token):
    user = User.verify_reset_credential_token(token)
    if not user:
        return flask.redirect(url_for('main.index'))
    
    form = ResetEmailForm()
    if form.validate_on_submit():
        user.emailAddress = form.email_address.data
        db.session.commit()
        flask.flash('Your email has been reset successfully')
        return flask.redirect(flask.url_for('authentication.login'))

    return flask.render_template('registration/reset_email.html', form = form)
