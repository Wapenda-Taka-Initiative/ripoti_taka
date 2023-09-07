import flask
import os
from flask_login import current_user
from . import registration
from .forms import RegistrationForm, EditUserProfileForm
from .. import db
from ..models import User


@registration.route('/edit_profile_image/<int:user_id>', methods = ['GET', 'POST'])
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
        flask.flash("Registration successful. Welcome to the revolution!!!")
        return flask.redirect(flask.url_for('authentication.login'))

    return flask.render_template('registration/register_user.html', form = form)


@registration.route('/edit_user_profile/<int:user_id>', methods = ['GET', 'POST'])
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
