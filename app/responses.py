import random

from app.config import (
    EMOJIS,
    MOOD_KEYWORDS, 
    STUDY_TIPS, 
    ENCOURAGEMENTS, 
    JOKES,
    FALLBACK_RESPONSES
)


# --------------------
# Helper Functions
# --------------------

def normalize_text(text: str) -> str:
    """
    Mormalize user input for easier matching.
    """
    return text.lower().strip()


def detect_mood(user_input: str):
    """
    Detect the user's mood based on keywords.
    Returns mood name or None.
    """
    for mood, keywords in MOOD_KEYWORDS.items():
        for keyword in keywords:
            if keyword in user_input:
                return mood
    return None


# -------------------------
# Response Generators
# -------------------------

def mood_response(mood: str) -> str:
    """
    Generate a supportive response based on detected mood.
    """
    emoji = random.choice(EMOJIS.get(mood, []))
    encouragement = random.choice(ENCOURAGEMENTS)

    if mood == "happy":
        return f"That's great to hear! {emoji} Keep that energy going!"
    elif mood == "sad":
        return f"I'm sorry you're feeling this way {emoji}. {encouragement}"
    elif mood == "stressed":
        return f"That sounds overwhelming {emoji}. {encouragement}"
    elif mood == "tired":
        return f"You might need some rest {emoji}. Don't forget to take breaks."
    

    return encouragement


def study_tip_response() -> str:
    """
    Provide a random study tip.
    """
    tip = random.choice(STUDY_TIPS)
    emoji = random.choice(EMOJIS["study"])
    return f"{tip} {emoji}"


def joke_response() -> str:
    """
    Tell a joke
    """
    joke = random.choice(JOKES)
    emoji = random.choice(EMOJIS["joke"])
    return f"{joke} {emoji}"


def fallback_response() -> str:
    """
    Default response if no intent is matched.
    """
    return random.choice(FALLBACK_RESPONSES)



# -----------------------
# Main Decision function
# -----------------------

def get_rule_based_response(user_input: str):
    """
    Main entry for rule-based chatbot response.
    Returns a response string or None.
    """
    if not user_input:
        return "Say something - I'm here for you 😊"
    
    text = normalize_text(user_input)


    # Mood detection
    mood = detect_mood(text)

    if mood:
        return mood_response(mood)
    
    # Study intent
    if any(word in text for word in ["study", "exam", "focus", "homework"]):
        return study_tip_response()

    # Joke intent
    if any(word in text for word in ["joke", "funny", "laugh"]):
        return joke_response()

    # No rule matched
    return fallback_response()