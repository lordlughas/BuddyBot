from typing import List, Dict
import re


TOPIC_KEYWORDS = {
    "budgeting": [
        "budget",
        "save",
        "saving",
        "expense",
        "spend",
        "debt",
        "emergency fund",
    ],
    "investing": [
        "invest",
        "portfolio",
        "stock",
        "etf",
        "bond",
        "mutual fund",
        "diversify",
    ],
    "retirement": [
        "retirement",
        "401k",
        "ira",
        "pension",
        "retire",
    ],
    "risk": [
        "risk",
        "volatile",
        "volatility",
        "drawdown",
        "loss",
        "hedge",
    ],
    "taxes": [
        "tax",
        "deduction",
        "capital gains",
        "taxable",
    ],
}


def _classify_topic(latest_user_message: str) -> str:
    text = (latest_user_message or "").lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return topic
    return "general_finance"


def build_financial_system_prompt(messages: List[Dict[str, str]]) -> str:
    latest_user_message = ""
    for message in reversed(messages):
        if message.get("role") == "user":
            latest_user_message = message.get("content", "")
            break

    topic = _classify_topic(latest_user_message)

    topic_guidance = {
        "budgeting": "Prioritize practical monthly budgeting, debt payoff order, and emergency fund steps.",
        "investing": "Explain diversification, time horizon, fees, and risk-return tradeoffs in plain language.",
        "retirement": "Focus on retirement planning basics, contribution strategy, and long-term compounding.",
        "risk": "Discuss downside scenarios and risk management before upside potential.",
        "taxes": "Share general tax-awareness tips and remind users to confirm details with local tax rules.",
        "general_finance": "Provide concise financial education and structured action steps.",
    }[topic]

    return (
        "You are Finsight AI, a Financial Advisory Assistant for educational guidance. "
        "Be practical, concise, and structured. Ask one clarifying question when key details are missing. "
        "Do not claim guaranteed returns, do not provide illegal or deceptive advice, and do not impersonate a licensed fiduciary. "
        "If advice could be jurisdiction-specific, say that rules vary by location. "
        "Always include a short risk note when discussing investments. "
        f"Current intent focus: {topic}. {topic_guidance}"
    )


def generate_chat_title(first_user_message: str, max_words: int = 7) -> str:
    text = (first_user_message or "").strip()
    if not text:
        return "New Chat"

    cleaned = re.sub(r"\s+", " ", text)
    cleaned = re.sub(r"[^\w\s$%-]", "", cleaned)
    words = cleaned.split()

    if not words:
        return "New Chat"

    short = " ".join(words[:max_words])
    return short[:60].strip()
