import imp
from flask import render_template,redirect,url_for,request,abort,current_app,flash
from flask_login import login_user, current_user,logout_user,login_required
from twittor.forms import LoginForm,RegisterForm,EditProfileForm,TweetForm,PasswordResetRequestForm,PasswordResetForm
from twittor.models.user import User
from twittor.models.tweet import Tweet
from twittor import db
from twittor.email import send_email


@login_required
def index():
    form = TweetForm()
    if form.validate_on_submit():
        tweet = Tweet(body=form.tweet.data,author=current_user)
        db.session.add(tweet)
        db.session.commit()
        return redirect(url_for('index'))
    page_num = int(request.args.get('page') or 1)
    tweets =current_user.own_and_followed_tweets().paginate(
        page=page_num,per_page=current_app.config['TWEET_PER_PAGE'],
        error_out=False)
    next_url = url_for(
        'index',page=tweets.next_num) if tweets.has_next else None
    prev_url = url_for(
        'index',page=tweets.prev_num) if tweets.has_prev else None
    return render_template('index.html',tweets=tweets.items,form=form,next_url=next_url,prev_url=prev_url)

def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        u =User.query.filter_by(username=form.username.data).first()
        if u is None or not u.check_password(form.password.data):
            print('user not exsited')
            return redirect(url_for('login'))
        login_user(u,remember=form.remember_me.data)
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
    return render_template('login.html',title="Login", form = form)

def logout():
    logout_user()
    return redirect(url_for('login'))

def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html',title = 'Registration',form=form)

@login_required
def user(username):
    u =User.query.filter_by(username=username).first()
    if u is None:
        return abort(404)
    page_num = int(request.args.get('page') or 1)
    tweets = u.tweet.order_by(Tweet.create_time.desc()).paginate(
        page=page_num,per_page=current_app.config['TWEET_PER_PAGE'],
        error_out=False)
    next_url = url_for(
        'profile',username=username,page=tweets.next_num) if tweets.has_next else None
    prev_url = url_for(
        'profile',username=username,page=tweets.prev_num) if tweets.has_prev else None
    if request.method == 'POST':
        if request.form['request_button'] == 'Follow':
            current_user.follow(u)
            db.session.commit()
        else:
            current_user.unfollow(u)
            db.session.commit()
            
    return render_template('user.html',title='Profile',tweets=tweets.items,user=u,next_url=next_url,prev_url=prev_url)

@login_required
def edit_profile():
    form = EditProfileForm()
    if request.method == 'GET':
        form.about_me.data = current_user.about_me
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('profile',username=current_user.username))
    return render_template('edit_profile.html',form=form)

def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash(
                "You should soon receive an email allowing you ro rest your \
                password. Please make sure to check your spam and trash \
                if you can't find the email."
            )
            token = user.get_jwt()
            url_password_reset = url_for(
                'password_reset',
                token=token,
                _external=True
            )
            url_password_reset_request = url_for(
                'reset_password_request',
                _external=True
            )
            send_email(
                subject=current_app.config['MAIL_SUBJECT_RESET_PASSWORD'],
                recipients=[user.email],
                text_body=render_template(
                    'email/password_reset.txt',
                    url_password_reset=url_password_reset,
                    url_password_reset_request=url_password_reset_request
                ),
                html_body=render_template(
                    'email/password_reset.html',
                    url_password_reset=url_password_reset,
                    url_password_reset_request=url_password_reset_request
                )
            )
        else:
            raise
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',form=form)

def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user =User.verify_jwt(token)
    if not user:
        return redirect(url_for('login'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('password_reset.html',title='Password Reset', form=form)
    
def page_not_found(e):
    return render_template('404.html'),404

@login_required
def explore():
    page_num = int(request.args.get('page') or 1)
    tweets =Tweet.query.order_by(Tweet.create_time.desc()).paginate(
        page=page_num,per_page=current_app.config['TWEET_PER_PAGE'],
        error_out=False)
    next_url = url_for(
        'explore',page=tweets.next_num) if tweets.has_next else None
    prev_url = url_for(
        'explore',page=tweets.prev_num) if tweets.has_prev else None
    return render_template(
        'explore.html',tweets=tweets.items,next_url=next_url,prev_url=prev_url
        )