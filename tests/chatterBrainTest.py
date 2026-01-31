from app.responses import get_rule_based_response
from app.chatter import BuddyBotAI

ai_bot = BuddyBotAI()

def chat(user_input):
    rule_response = get_rule_based_response(user_input)
    if(rule_response):
        return rule_response
    return ai_bot.get_response(user_input)


print(chat("I feel sad"))
print(chat("Tell me a joke"))
print(chat("What is Information Technology?"))