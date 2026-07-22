import os
import sys

# Add parent directory to path so we can import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, storage_uri='memory://')


def create_app(config_class=Config):
    web_root = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(web_root, 'templates'),
        static_folder=os.path.join(web_root, 'static'),
    )
    app.config.from_object(config_class)

    # Trust X-Forwarded-* from Railway, Vercel, and nginx
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from blueprints.main import main_bp
    from blueprints.auth import auth_bp
    from blueprints.generator import generator_bp
    from blueprints.api_docs import api_docs_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(generator_bp, url_prefix='/generator')
    app.register_blueprint(api_docs_bp, url_prefix='/docs')

    # Create database tables (skip hard crash if DB is briefly unreachable)
    with app.app_context():
        try:
            db.create_all()
        except Exception as exc:
            app.logger.exception('Database init failed: %s', exc)
            if os.environ.get('VERCEL') or os.environ.get('RAILWAY_ENVIRONMENT'):
                raise RuntimeError(
                    'Database init failed. Set a reachable DATABASE_URL '
                    '(Postgres recommended on Vercel/Railway).'
                ) from exc

    return app


if __name__ == '__main__':
    app = create_app()
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug, port=5000)
