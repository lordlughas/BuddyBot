import jwt
from datetime import datetime, timedelta
from flask import current_app
from functools import wraps
from flask import request, jsonify
from app.models.user import User

def generate_token(user):
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(
            seconds=current_app.config["JWT_EXPIRES_IN"]
        )
    }

    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET"],
        algorithm="HS256"
    )

    return token

def decode_token(token):
    return jwt.decode(
        token,
        current_app.config["JWT_SECRET"],
        algorithms=["HS256"]
    )

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")

        if not token:
            return jsonify({"error": "Authentication required"}), 401

        try:
            data = decode_token(token)
            user = User.query.get(data["user_id"])
            if not user:
                raise Exception("User not found")
        except Exception:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated



# print("SECRET_KEY:", current_app.config.get("SECRET_KEY"))
# print("JWT_SECRET:", current_app.config.get("JWT_SECRET"))