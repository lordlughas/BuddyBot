from flask import Blueprint, request, render_template, jsonify
#from app.security.tokens import login_required
from app.ai.openai_client import get_ai_response
from app.database.db import db
from flask_login import login_required, current_user
from app.models.chat import Chat
from app.models.message import Message

chat_bp = Blueprint("chat", __name__)

# Chat Page (GET)
@chat_bp.route("/chat", methods=["GET"])
@login_required
def chat_page():
    return render_template("chat/chat.html")


@chat_bp.route("/settings")
@login_required
def settings():
    return render_template("settings.html")

# API endpoint for AI (POST)
# @chat_bp.route("/chat", methods=["POST"])
# @login_required
# def send_message():
    # data = request.get_json()
    # user_message = data.get("message")

    # if not user_message:
    #     return jsonify({"error": "No message provided"}), 400

    # messages = [
    #     {
    #         "role": "system",
    #         "content": "You are BuddyBot, a helpful financial AI assistant."
    #     },
    #     {
    #         "role": "user",
    #         "content": user_message
    #     }
    # ]

    # ai_reply = get_ai_response(messages)

    # return jsonify({"reply": ai_reply})

@chat_bp.route("/chat", methods=["POST"])
@login_required
def send_message():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    user_message = data.get("message")
    chat_id = data.get("chat_id")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # print("Authenticated:", current_user.is_authenticated)
    # print("User:", current_user)


    # If no chat, create new one
    if not chat_id:
        chat = Chat(
            user_id=current_user.id,
            title="New Chat"
        )
        db.session.add(chat)
        db.session.commit()
    else:
        chat = Chat.query.filter_by(
            id=chat_id,
            user_id=current_user.id  # 🔥 security check
        ).first()

        if not chat:
            return jsonify({"error": "Chat not found"}), 404

    # Save user message
    user_msg = Message(
        chat_id=chat.id,
        role="user",
        content=user_message
    )
    db.session.add(user_msg)
    db.session.commit()  # commit before AI call for safety

    # Load previous messages for context
    history = Message.query.filter_by(chat_id=chat.id)\
                           .order_by(Message.created_at.asc())\
                           .all()

    formatted_messages = [
        {"role": m.role, "content": m.content}
        for m in history
    ]

    # Get AI response
    ai_reply = get_ai_response(formatted_messages)

    # Save AI response
    ai_msg = Message(
        chat_id=chat.id,
        role="assistant",
        content=ai_reply
    )
    db.session.add(ai_msg)

    # Auto-generate title if first message
    if chat.title == "New Chat":
        chat.title = user_message[:40]

    db.session.commit()

    return jsonify({
        "reply": ai_reply,
        "chat_id": chat.id
    })

@chat_bp.route("/conversations", methods=["GET"])
@login_required
def get_conversations():
    chats = Chat.query.filter_by(
        user_id=current_user.id
    ).order_by(Chat.created_at.desc()).all()

    return jsonify([
        {
            "id": c.id,
            "title": c.title
        }
        for c in chats
    ])


@chat_bp.route("/conversations/<int:conv_id>", methods=["GET"])
@login_required
def get_conversation(conv_id):
    messages = Message.query.filter_by(chat_id=conv_id).all()

    return jsonify([
        {
            "role": m.role,
            "content": m.content
        }
        for m in messages
    ])


