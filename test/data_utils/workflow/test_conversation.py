import json

from data import BotOutput, Message, Role, Conversation


def test_message():
    for role in (Role.USER, "custom_role"):
        msg = Message(role=role, content="hello")
        print(msg)


def test_add_message():
    conv = Conversation()

    conv.add_message(Message(role=Role.USER, content="hello"))
    conv.add_message(msg="hello", role=Role.USER)
    print(conv)
    print()


def test_custom_role():
    msg = Message(role="user", content="hello")
    print(msg, msg.role)

    msg = Message(role="custom_role", content="hello")
    print(msg, msg.role)


def test_bot_output():
    bot_output = BotOutput(
        thought="...",
        action="check_hospital_exist",
        action_input={"test": "test"},
        response=None,
    )
    print(json.dumps(bot_output, ensure_ascii=False))
    print(bot_output)


# test_custom_role()
test_bot_output()
print()
