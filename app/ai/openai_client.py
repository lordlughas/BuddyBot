from openai import OpenAI
from flask import current_app
from app.ai.finance_router import build_financial_system_prompt

# def get_ai_response(message):
#     """
#     messages = [
#         {"role": "system", "content": "..."},
#         {"role": "user", "content": "..."},
#     ]
#     """

#     client = OpenAI(
#         api_key=current_app.config["OPENAI_API_KEY"]
#     )

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",  # fast + affordable
#         #messages=messages,
#         messages=[
#             {"role": "system", "content": "You are a financial assistant."},
#             {"role": "user", "content": message}
#         ],
#         temperature=0.7,
#     )

#     return response.choices[0].message.content
def get_ai_response(messages):
    return "".join(stream_ai_response(messages)).strip() or "I could not generate a response right now."


def stream_ai_response(messages):
    api_key = current_app.config.get("OPENAI_API_KEY")
    if not api_key:
        yield "OpenAI API key is missing. Add OPENAI_API_KEY in your environment settings."
        return

    client = OpenAI(api_key=api_key)
    system_prompt = build_financial_system_prompt(messages)

    recent_messages = messages[-12:] if len(messages) > 12 else messages
    completion_messages = [{"role": "system", "content": system_prompt}] + recent_messages

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=completion_messages,
        temperature=0.3,
        stream=True,
    )

    for chunk in stream:
        choices = getattr(chunk, "choices", None) or []
        if not choices:
            continue

        delta = getattr(choices[0], "delta", None)
        content = getattr(delta, "content", None) if delta else None
        if content:
            yield content
