from flowagent.data import Conversation, Message, Role, BotOutput
import json

def test_custom_role():
    msg = Message(role="user", content="hello")
    print(msg, msg.role)

    msg = Message(role="custom_role", content="hello")
    print(msg, msg.role)

def test_bot_output():
    bot_output = BotOutput(thought="...", action="check_hospital_exist", action_input={"test": "test"}, response=None)
    print(json.dumps(bot_output, ensure_ascii=False))
    print(bot_output)

# test_custom_role()
test_bot_output()
print()
