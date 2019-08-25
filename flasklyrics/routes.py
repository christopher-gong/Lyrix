import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flasklyrics import app, bcrypt, db
from flasklyrics.forms import RegistrationForm, LoginForm, SearchForm, UpdateAccountForm, RhymeForm
from flasklyrics.models import User, Rhyme
from flask_login import login_user, current_user, logout_user, login_required
from flasklyrics.addDB import addWord, getRhyme

@app.route("/")
@app.route("/home")
def home():
    searchform = SearchForm()
    rhymes = Rhyme.query.all()
    phrase = request.args.get('phrase')
    if (phrase):
        print(phrase)
        rhymes = getRhyme(phrase)
        #print(Rhyme.query.all())
        print(rhymes)
        return render_template('rhyme.html', phrase = phrase, rhymes = rhymes, searchform = searchform)
    return render_template('home.html', rhymes = rhymes, searchform = searchform)

@app.route("/about")
def about():
    searchform = SearchForm()
    return render_template('about.html', title = "About", searchform = searchform)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    searchform = SearchForm()
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Welcome to Lryix, {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form = form, searchform = searchform)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash('Sorry, Lyrix could not verify these credentials. Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Lyrix account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/rhyme/new", methods=['GET', 'POST'])
@login_required
def new_rhyme():
    form = RhymeForm()
    if form.validate_on_submit():
        #rhyme = Rhyme(phrase=form.phrase.data, author=current_user)
        #db.session.add(rhyme)
        addWord(form.phrase.data, current_user)
        db.session.commit()
        flash('Your rhyme has been added!', 'success')
        return redirect(url_for('home'))
    return render_template('create_rhyme.html', title='New Rhyme', form=form)

#@app.route("/rhyme/<int:rhyme_id>")
#def rhyme(rhyme_id):
#    searchform = SearchForm()
#    rhyme = Rhyme.query.get_or_404(post_id)
#    return render_template('rhyme.html', rhyme=rhyme, searchform = SearchForm)