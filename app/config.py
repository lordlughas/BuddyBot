import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")

    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_EXPIRES_IN = 1800  # 30 minutes

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    MAIL_SENDER = os.getenv("MAIL_SENDER")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# =========================
# BuddyBot Personality Config
# =========================

BOT_NAME = "BuddyBot"

BOT_DESCRIPTION = (
    "A friendly peer and study buddy who supports students emotionally "
    "and academically in a casual, human-like way."
)

# -------------------------
# Emojis for Expression
# -------------------------

EMOJIS = {
    "happy": ["😄", "😊", "🎉"],
    "sad": ["😔", "💙", "☁️"],
    "stressed": ["😣", "💭", "😵"],
    "tired": ["😴", "☕", "🛌"],
    "encourage": ["💪", "🔥", "✨"],
    "study": ["📚", "📝", "🧠"],
    "joke": ["😂", "🤣", "😆"]
}

# -------------------------
# Mood Detection Keywords
# -------------------------

MOOD_KEYWORDS = {
    "happy": ["happy", "great", "awesome", "good", "excited"],
    "sad": ["sad", "down", "unhappy", "depressed", "lonely"],
    "stressed": ["stressed", "overwhelmed", "pressure", "anxious"],
    "tired": ["tired", "sleepy", "exhausted", "burnt out"]
}

# -------------------------
# Study Tips
# -------------------------

STUDY_TIPS = [
    "Try the Pomodoro technique: 25 minutes study, 5 minutes break.",
    "Break big tasks into smaller, manageable chunks.",
    "Studying a little every day beats cramming.",
    "Teach what you learn to someone else — it really helps!",
    "Make sure you stay hydrated while studying."
]

# -------------------------
# Encouragement Messages
# -------------------------

ENCOURAGEMENTS = [
    "You’ve got this! One step at a time.",
    "Progress is progress — even small steps count.",
    "I believe in you. Keep going!",
    "It’s okay to struggle. That means you’re learning.",
    "You’re doing better than you think."
]

# -------------------------
# Jokes
# -------------------------

JOKES = [
    "Why did the math book look sad? Because it had too many problems.",
    "Why don’t scientists trust atoms? Because they make up everything.",
    "Why was the computer cold? It forgot to close its Windows.",
    "Why did the student eat their homework? Because the teacher said it was a piece of cake!"
]

# -------------------------
# Fallback Responses
# -------------------------

FALLBACK_RESPONSES = [
    "Hmm, I’m not sure I understood that — could you rephrase?",
    "Interesting! Tell me a bit more.",
    "I’m still learning, but I’d love to hear more about that.",
    "Can you explain that in another way?",
    "I think you should give me more context, so I can assist better",
    "Hmm 🤔 tell me more about that",
    "I'm listening 👂",
    "Can you explain a bit more? 😊",
    "Interesting… go on!"
]


# ------------------------
# Bot Personality
# ------------------------

BOT_PERSONALITY = {
    "name":"BuddyBot",
    "tone": "friendly",
    "signature": "😊"
}