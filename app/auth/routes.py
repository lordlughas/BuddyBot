from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from app.database.db import db
from app.models.user import User
#from app.security.tokens import login_required
from flask_login import login_required, login_user, current_user
from app.security.hashing import hash_password, verify_password
from app.security.tokens import generate_token
from app.auth.utils import (
    generate_reset_token,
    hash_reset_token,
    reset_token_expiry
)
from datetime import datetime
from flask import render_template
from flask import make_response


auth_bp = Blueprint("auth", __name__)
#chat_bp = Blueprint("chat", __name__)





#REGISTER

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400
    
    user = User(
        full_name=data["full_name"],
        email=data["email"],
        password_hash=hash_password(data["password"]),
    )

    db.session.add(user)
    db.session.commit()

    token = generate_token(user)

    response = make_response(jsonify({"message": "Registered successfully"}))
    response.set_cookie("access_token", token, httponly=True, samesite="Lax")
    return response


    # return jsonify({"token": token})



#LOGIN
# @auth_bp.route("/login", methods=["POST"])
# def login():
#     data = request.json

#     user = User.query.filter_by(email=data["email"]).first()

#     if not user or not user.password_hash:
#         return jsonify({"error": "Invalid credentials"}), 401
    
#     if not verify_password(data["password"], user.password_hash):
#         return jsonify({"error": "Invalid credentials"}), 401
    
#     token = generate_token(user)

#     return jsonify({"token": token})


# #Redirect route pages
# @chat_bp.route("/chat")
# @login_required
# def chat_page():
#     return render_template("chat/chat.html")



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


# @auth_bp.route("/login", methods=["GET"])
# def login():
#     return render_template("auth/login.html")

#Routes
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.password_hash:
        return jsonify({"error": "Invalid credentials"}), 401

    if not verify_password(data["password"], user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user)
    login_user(user)
    response = make_response(jsonify({"message": "Login successful"}))
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure=False,  # Change to True in production
        samesite="Lax",
        max_age=1800
    )

    return response



from app.auth.google_oauth import get_google_client

#GOOGLE LOGIN
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
            full_name=user_info["name"],
            email=user_info["email"],
            google_id=user_info["sub"],
            auth_provider="google"
        )

        db.session.add(user)
        db.session.commit()

    jwt_token = generate_token(user)

    return jsonify({"token": jwt_token})



#FORGET PASSWORD
@auth_bp.route("/forget-password", methods=["POST"])
def forgot_password():
    email = request.json["email"]

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "If email exists, reset link sent"})
    

    token = generate_reset_token()

    user.reset_token_hash = hash_reset_token(token)
    user.reset_token_expiry = reset_token_expiry()

    db.session.commit()


    # TODO: Send email with reset link
    print(f"Reset link: /reset-password/{token}")

    return jsonify({"message": "Reset link sent"})



#RESET PASSWORD
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json

    token_hash = hash_reset_token(data["token"])

    user = User.query.filter_by(reset_token_hash=token_hash).first()

    if not user or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Invalid or expired token"}), 400

    user.password_hash = hash_password(data["new_password"])
    user.reset_token_hash = None
    user.reset_token_expiry = None

    db.session.commit()

    return jsonify({"message": "Password reset successful"})



@auth_bp.route("/logout")
def logout():
    response = make_response(redirect("/auth/login-page"))
    response.delete_cookie("access_token")
    return response
