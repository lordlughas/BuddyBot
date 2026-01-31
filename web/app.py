from flask import Flask, render_template, jsonify, request, session
from app.responses import get_rule_based_response
import secrets
from app.chatter import BuddyBotAI


def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16) # session security
    bot_ai = BuddyBotAI()

    @app.route("/")
    def index():
        return render_template("chat.html")
    
    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.get_json()
        user_message = data.get("message", "")

        # Initialize chat history
        if "history" not in session:
            session["history"] = []

        session["history"].append({"user": user_message})

        # Phase 4 logic (simple for now)
        bot_reply = get_rule_based_response(user_message)

        session["history"].append({"bot": bot_reply})

        session.modified = True

        return jsonify({
            "reply": bot_reply
        })

    return app
