from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse

from app import db, limiter
from models import User
from forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        flash('Welcome back!', 'success')
        return redirect(next_page)

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit('5 per minute')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.generate_api_key()
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')


@auth_bp.route('/regenerate-api-key', methods=['POST'])
@login_required
def regenerate_api_key():
    current_user.generate_api_key()
    db.session.commit()
    flash('API key regenerated successfully.', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/kaggle-credentials', methods=['POST'])
@login_required
def save_kaggle_credentials():
    username = request.form.get('kaggle_username', '').strip()
    key = request.form.get('kaggle_key', '').strip()

    if not username or not key:
        flash('Both a Kaggle username and API key are required.', 'danger')
        return redirect(url_for('auth.profile'))

    current_user.set_kaggle_credentials(username, key)
    db.session.commit()
    flash('Kaggle credentials saved.', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/kaggle-credentials/remove', methods=['POST'])
@login_required
def remove_kaggle_credentials():
    current_user.clear_kaggle_credentials()
    db.session.commit()
    flash('Kaggle credentials removed.', 'info')
    return redirect(url_for('auth.profile'))
