from app.database.db import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(120), nullable=True)

    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)

    google_id = db.Column(db.String(255), nullable=True)
    auth_provider = db.Column(db.String(50), default="local")

    reset_token_hash = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chats = db.relationship("Chat", backref="user", lazy=True)
