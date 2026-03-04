from flask import Blueprint, request, render_template, jsonify, Response, stream_with_context, redirect
from flask_login import login_required, current_user

from app.ai.openai_client import get_ai_response, stream_ai_response
from app.ai.prompt_suggester import generate_predictive_prompts
from app.ai.finance_router import generate_chat_title
from app.database.db import db
from app.models.chat import Chat
from app.models.message import Message


chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/", methods=["GET"])
def home_page():
    if current_user.is_authenticated:
        return redirect("/chat")
    return render_template("home.html")


@chat_bp.route("/privacy", methods=["GET"])
def privacy_page():
    return render_template("privacy.html")


@chat_bp.route("/terms", methods=["GET"])
def terms_page():
    return render_template("terms.html")


@chat_bp.route("/contact", methods=["GET"])
def contact_page():
    return render_template("contact.html")


@chat_bp.route("/chat", methods=["GET"])
@login_required
def chat_page():
    return render_template("chat/chat.html")


@chat_bp.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


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

    chat = _get_or_create_chat(chat_id, user_message)
    if isinstance(chat, tuple):
        return chat

    _save_user_message(chat.id, user_message)

    history = Message.query.filter_by(chat_id=chat.id).order_by(Message.created_at.asc()).all()
    formatted_messages = [{"role": m.role, "content": m.content} for m in history]

    ai_reply = get_ai_response(formatted_messages)

    db.session.add(
        Message(
            chat_id=chat.id,
            role="assistant",
            content=ai_reply,
        )
    )
    db.session.commit()

    suggestions = generate_predictive_prompts(
        formatted_messages + [{"role": "assistant", "content": ai_reply}]
    )

    return jsonify(
        {
            "reply": ai_reply,
            "chat_id": chat.id,
            "suggestions": suggestions,
        }
    )


@chat_bp.route("/chat/stream", methods=["POST"])
@login_required
def stream_message():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    user_message = data.get("message")
    chat_id = data.get("chat_id")
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    chat = _get_or_create_chat(chat_id, user_message)
    if isinstance(chat, tuple):
        return chat

    _save_user_message(chat.id, user_message)

    history = Message.query.filter_by(chat_id=chat.id).order_by(Message.created_at.asc()).all()
    formatted_messages = [{"role": m.role, "content": m.content} for m in history]

    @stream_with_context
    def generate():
        chunks = []
        try:
            for token in stream_ai_response(formatted_messages):
                if token:
                    chunks.append(token)
                    yield token
        finally:
            full_reply = "".join(chunks).strip()
            if full_reply:
                db.session.add(
                    Message(
                        chat_id=chat.id,
                        role="assistant",
                        content=full_reply,
                    )
                )
                db.session.commit()

    response = Response(generate(), mimetype="text/plain")
    response.headers["X-Chat-Id"] = str(chat.id)
    return response


@chat_bp.route("/conversations", methods=["GET"])
@login_required
def get_conversations():
    chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.created_at.desc()).all()
    return jsonify([{"id": c.id, "title": c.title} for c in chats])


@chat_bp.route("/conversations/<int:conv_id>", methods=["GET"])
@login_required
def get_conversation(conv_id):
    chat = Chat.query.filter_by(id=conv_id, user_id=current_user.id).first()
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    messages = Message.query.filter_by(chat_id=conv_id).order_by(Message.created_at.asc()).all()
    return jsonify([{"role": m.role, "content": m.content} for m in messages])


@chat_bp.route("/prompt-suggestions", methods=["GET"])
@login_required
def get_prompt_suggestions():
    chat_id = request.args.get("chat_id", type=int)
    if not chat_id:
        return jsonify({"suggestions": generate_predictive_prompts([])})

    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first()
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at.asc()).all()
    formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
    return jsonify({"suggestions": generate_predictive_prompts(formatted_messages)})


def _get_or_create_chat(chat_id, user_message):
    if not chat_id:
        chat = Chat(user_id=current_user.id, title=generate_chat_title(user_message))
        db.session.add(chat)
        db.session.commit()
        return chat

    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first()
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
    return chat


def _save_user_message(chat_id, user_message):
    db.session.add(
        Message(
            chat_id=chat_id,
            role="user",
            content=user_message,
        )
    )
    db.session.commit()
