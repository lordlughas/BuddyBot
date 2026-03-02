from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix
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
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.config.from_object(Config)
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    db.init_app(app)
    migrate.init_app(app, db)

    init_google_oauth(app)

     # Initialize extensions
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/chat") or request.path.startswith("/auth/"):
            if request.is_json or "application/json" in (request.headers.get("Accept") or ""):
                return jsonify({"error": "Authentication required"}), 401
        return render_template(
            "errors/error.html",
            status_code=401,
            title="Authentication Required",
            message="Please sign in to continue.",
        ), 401
    
    app.register_blueprint(chat_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.after_request
    def disable_static_cache(response):
        if request.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            response.headers.pop("ETag", None)
        return response

    def wants_json():
        if request.path.startswith("/chat") or request.path.startswith("/auth/"):
            return request.is_json or "application/json" in (request.headers.get("Accept") or "")
        return request.is_json or (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        )

    @app.errorhandler(404)
    def not_found(error):
        if wants_json():
            return jsonify({"error": "Resource not found"}), 404
        return render_template(
            "errors/error.html",
            status_code=404,
            title="Page Not Found",
            message="The page you requested does not exist or may have moved.",
        ), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        if wants_json():
            return jsonify({"error": "Method not allowed"}), 405
        return render_template(
            "errors/error.html",
            status_code=405,
            title="Method Not Allowed",
            message="This action is not available for that page.",
        ), 405

    @app.errorhandler(Exception)
    def handle_exception(error):
        if isinstance(error, HTTPException):
            return error

        app.logger.exception("Unhandled exception", exc_info=error)
        if wants_json():
            return jsonify({"error": "Internal server error"}), 500
        return render_template(
            "errors/error.html",
            status_code=500,
            title="Something Went Wrong",
            message="An unexpected error occurred. Please try again.",
        ), 500

    return app
