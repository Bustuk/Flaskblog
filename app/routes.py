from flask import render_template, url_for, flash, redirect,request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image


posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'WOLOLO',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }

]



@app.route('/')
@app.route('/home')
def root():
    return render_template('homepage.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():

    '''
    Route for new users registration,
    user model in models.py,
    validators in forms.py class: RegistrationForm
    :return: homepage if already logged, homepage if registered successfully,
             registration page if registered unsuccessfully
    '''

    if current_user.is_authenticated:
        #checking if user is already logged in, if so he will be redirected to homepage
        return redirect(url_for('root'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # bcrypt module is used in order to keep password hashed, not as plain text like Instagram
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('root'))

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'Post'])
def login():

    '''
    Route to log in user
    :return: page when user entered unauthorized if logged in succesfully,
             homepage if try to log in directly from /login,
             login page if logged unsuccessfully
    '''

    if current_user.is_authenticated:
        return redirect(url_for('root'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # bcrypt must be used cause passwords are encrypted
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('root'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')


    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect((url_for('root')))


def save_picture(form_picture):
    ''' Function to save pictures uploaded by the user in static/profile_pics,
     with a randomized filenames, so names provided by users don't matter'''
    random_hex_name = secrets.token_hex(8)
    # function returns pathname in a pair(root,ext) but the custom path will be created later,
    # so underscope is to "get rid of" useless value
    _, file_extension = os.path.splitext(form_picture.filename)


    picture_filename = random_hex_name + file_extension
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)

    #the maximum size of profile picture is 125x125 so user's profile pictures are resized in order to save disk space
    output_size = (125, 125)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)

    #TODO write some code which delete old profile picture, after succesfully updating it
    return picture_filename

@app.route('/account', methods=['GET','POST'])
@login_required
def account():

    '''
    Route to manage user account

    From this place profile picture, username and email can be changed.
    Validators for username and email all similar to the one during registration
    Profile pictures must be .jpg or or .png
    and will be resized to 125x125 to save disk space
    if no picture is provided, the default one is being chosen
    :return: account page
    '''

    form = UpdateAccountForm()
    if form.validate_on_submit(): #checking if provided text data is proper
        if form.picture.data:     #checking if user provided profile picture
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename=('profile_pics/'+ current_user.image_file))
    return render_template('account.html', title='Account', image_file=image_file, form=form )