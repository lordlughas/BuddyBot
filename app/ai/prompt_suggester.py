from typing import List, Dict


STARTER_SUGGESTIONS = [
    "Build me a simple monthly budget for a $3,500 income.",
    "How should a beginner start investing with low risk?",
    "Help me create a debt payoff strategy.",
    "What should be in my emergency fund plan?",
]


TOPIC_SUGGESTIONS = {
    "budget": [
        "Can you categorize fixed vs variable expenses for me?",
        "Help me cut 15% from my monthly spending.",
        "Create a 50/30/20 budget from my income.",
    ],
    "debt": [
        "Should I use avalanche or snowball for my debt?",
        "Help me prioritize these loan balances.",
        "How much extra should I pay monthly to clear debt faster?",
    ],
    "invest": [
        "Create a beginner diversified portfolio example.",
        "Explain ETFs vs mutual funds for long-term investing.",
        "How should I allocate investments by risk level?",
    ],
    "retire": [
        "How much should I save monthly for retirement?",
        "Explain 401(k) and IRA differences simply.",
        "What retirement assumptions should I use?",
    ],
    "tax": [
        "What records should I keep for tax season?",
        "Explain capital gains tax basics.",
        "How can I plan for taxes on investments?",
    ],
}


def _get_last_user_text(messages: List[Dict[str, str]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            return message.get("content", "").lower()
    return ""


def _pick_topic(text: str) -> str:
    if any(word in text for word in ["budget", "expense", "save", "saving", "spend"]):
        return "budget"
    if any(word in text for word in ["debt", "loan", "credit card"]):
        return "debt"
    if any(word in text for word in ["invest", "portfolio", "stock", "etf", "bond"]):
        return "invest"
    if any(word in text for word in ["retire", "retirement", "401k", "ira", "pension"]):
        return "retire"
    if any(word in text for word in ["tax", "deduction", "capital gains"]):
        return "tax"
    return ""


def generate_predictive_prompts(messages: List[Dict[str, str]], limit: int = 4) -> List[str]:
    if not messages:
        return STARTER_SUGGESTIONS[:limit]

    last_user_text = _get_last_user_text(messages)
    topic = _pick_topic(last_user_text)
    if topic:
        return TOPIC_SUGGESTIONS[topic][:limit]

    return [
        "Can you turn this into a step-by-step action plan?",
        "What assumptions are we making here?",
        "What are the main risks and how do I reduce them?",
        "Can you summarize this in 3 bullet points?",
    ][:limit]
