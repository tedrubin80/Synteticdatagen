from flask import Blueprint, render_template
from flask_login import current_user, login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/pricing')
def pricing():
    return render_template('pricing.html')


@main_bp.route('/developers')
def developers():
    return render_template('developers.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    from models import GenerationHistory
    recent_history = GenerationHistory.query.filter_by(user_id=current_user.id)\
        .order_by(GenerationHistory.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', recent_history=recent_history)
