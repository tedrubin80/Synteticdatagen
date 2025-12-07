from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_pro = db.Column(db.Boolean, default=False)

    # Usage tracking
    api_key = db.Column(db.String(64), unique=True, index=True)
    requests_today = db.Column(db.Integer, default=0)
    total_requests = db.Column(db.Integer, default=0)
    last_request_date = db.Column(db.Date)

    # Relationships
    generation_history = db.relationship('GenerationHistory', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_api_key(self):
        import secrets
        self.api_key = secrets.token_hex(32)
        return self.api_key

    def get_daily_limit(self):
        from config import Config
        return Config.PRO_TIER_LIMIT if self.is_pro else Config.FREE_TIER_LIMIT

    def get_max_rows(self):
        from config import Config
        return Config.MAX_ROWS_PRO if self.is_pro else Config.MAX_ROWS_FREE

    def can_make_request(self):
        from datetime import date
        today = date.today()
        if self.last_request_date != today:
            self.requests_today = 0
            self.last_request_date = today
        return self.requests_today < self.get_daily_limit()

    def increment_usage(self):
        from datetime import date
        today = date.today()
        if self.last_request_date != today:
            self.requests_today = 0
            self.last_request_date = today
        self.requests_today += 1
        self.total_requests += 1

    def __repr__(self):
        return f'<User {self.username}>'


class GenerationHistory(db.Model):
    __tablename__ = 'generation_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rows_generated = db.Column(db.Integer, nullable=False)
    output_format = db.Column(db.String(10), nullable=False)
    field_config = db.Column(db.JSON, nullable=False)

    def __repr__(self):
        return f'<GenerationHistory {self.id} - {self.rows_generated} rows>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
