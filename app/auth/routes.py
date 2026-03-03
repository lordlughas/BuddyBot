from datetime import datetime

from flask import Blueprint, current_app, jsonify, make_response, redirect, render_template, request, session, url_for
from flask_login import login_user, logout_user

from app.auth.google_oauth import get_google_client
from app.auth.utils import generate_reset_token, hash_reset_token, reset_token_expiry
from app.database.db import db
from app.models.user import User
from app.security.hashing import hash_password, verify_password
from app.security.tokens import generate_token


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not full_name or not email or not password:
        return jsonify({"error": "Full name, email, and password are required"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        auth_provider="local",
    )
    db.session.add(user)
    db.session.commit()

    token = generate_token(user)
    login_user(user)

    response = make_response(jsonify({"message": "Registered successfully"}))
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure=current_app.config.get("COOKIE_SECURE", True),
        samesite=current_app.config.get("SESSION_COOKIE_SAMESITE", "Lax"),
        max_age=1800,
    )
    return response


@auth_bp.route("/login-page")
def login_page():
    return render_template("auth/login.html")


@auth_bp.route("/register-page")
def register_page():
    return render_template("auth/register.html")


@auth_bp.route("/forgot-password-page")
def forgot_password_page():
    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password-page")
def reset_password_page():
    return render_template("auth/reset_password.html")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.password_hash:
        return jsonify({"error": "Invalid credentials"}), 401
    if not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user)
    login_user(user)

    response = make_response(jsonify({"message": "Login successful"}))
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure=current_app.config.get("COOKIE_SECURE", True),
        samesite=current_app.config.get("SESSION_COOKIE_SAMESITE", "Lax"),
        max_age=1800,
    )
    return response


@auth_bp.route("/login/google")
def google_login():
    google = get_google_client()
    redirect_uri = url_for("auth.google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route("/login/google/callback")
def google_callback():
    google = get_google_client()
    token = google.authorize_access_token()
    user_info = google.parse_id_token(token)

    user = User.query.filter_by(email=user_info["email"]).first()
    if not user:
        user = User(
            full_name=user_info.get("name"),
            email=user_info["email"],
            google_id=user_info.get("sub"),
            auth_provider="google",
        )
        db.session.add(user)
        db.session.commit()

    jwt_token = generate_token(user)
    login_user(user)

    response = make_response(redirect("/chat"))
    response.set_cookie(
        "access_token",
        jwt_token,
        httponly=True,
        secure=current_app.config.get("COOKIE_SECURE", True),
        samesite=current_app.config.get("SESSION_COOKIE_SAMESITE", "Lax"),
        max_age=1800,
    )
    return response


@auth_bp.route("/forgot-password", methods=["POST"])
@auth_bp.route("/forget-password", methods=["POST"])  # backward compatibility
def forgot_password():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()

    generic_message = "If an account exists, a password reset link has been sent."
    if not email:
        return jsonify({"message": generic_message}), 200

    user = User.query.filter_by(email=email).first()
    token_for_link = generate_reset_token()

    if user:
        user.reset_token_hash = hash_reset_token(token_for_link)
        user.reset_token_expiry = reset_token_expiry()
        db.session.commit()

    reset_link = url_for("auth.reset_password_page", token=token_for_link, _external=True)
    if current_app.config.get("MOCK_EMAIL_ENABLED", True):
        current_app.logger.info("MOCK password reset link for %s: %s", email, reset_link)
        return jsonify(
            {
                "message": generic_message,
                "mock_reset_link": reset_link,
            }
        ), 200

    return jsonify({"message": generic_message}), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json or {}
    token = (data.get("token") or "").strip()
    new_password = data.get("new_password") or ""

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400
    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    token_hash = hash_reset_token(token)
    user = User.query.filter_by(reset_token_hash=token_hash).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Invalid or expired token"}), 400

    # Generates a fresh salted hash and invalidates reset token.
    user.password_hash = hash_password(new_password)
    user.reset_token_hash = None
    user.reset_token_expiry = None
    db.session.commit()

    return jsonify({"message": "Password reset successful"})


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    session.clear()
    wants_json = (
        request.is_json
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        )
    )

    response = (
        make_response(jsonify({"message": "Logged out"}))
        if wants_json
        else make_response(redirect("/auth/login-page"))
    )
    response.delete_cookie("access_token")
    return response
