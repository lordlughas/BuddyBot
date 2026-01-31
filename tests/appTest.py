from app.config import BOT_NAME, STUDY_TIPS

print(BOT_NAME)
print(STUDY_TIPS[0])


from app.responses import get_rule_based_response

print(get_rule_based_response("I am really stressed about exams"))
print(get_rule_based_response("Give me a study tip"))
print(get_rule_based_response("Tell me a joke"))
print(get_rule_based_response("What is the meaning of life?"))
