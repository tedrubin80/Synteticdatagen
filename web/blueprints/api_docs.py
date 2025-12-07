from flask import Blueprint, render_template

api_docs_bp = Blueprint('api_docs', __name__)


@api_docs_bp.route('/')
def index():
    return render_template('docs/index.html')


@api_docs_bp.route('/authentication')
def authentication():
    return render_template('docs/authentication.html')


@api_docs_bp.route('/endpoints')
def endpoints():
    return render_template('docs/endpoints.html')


@api_docs_bp.route('/examples')
def examples():
    return render_template('docs/examples.html')
