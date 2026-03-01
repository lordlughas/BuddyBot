from flask import Flask
from app.database.db import db, migrate
from app.config import Config
from app.models.user import User
from app.models.chat import Chat
from app.models.message import Message
from app.auth.routes import auth_bp
from app.chat.routes import chat_bp
from app.auth.google_oauth import init_google_oauth
from .extensions import login_manager
import os


def create_app():
    #app = Flask(__name__)
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "web", "templates"),
        static_folder=os.path.join(base_dir, "web", "static")
    )
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    init_google_oauth(app)

     # Initialize extensions
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    app.register_blueprint(chat_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app
