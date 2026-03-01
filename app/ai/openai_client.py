from openai import OpenAI
from flask import current_app

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
    client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"])

    # Extract user message only
    user_message = messages[-1]["content"]

    response = client.responses.create(
        model="gpt-4o-mini",
        input=user_message
    )

    return response.output_text