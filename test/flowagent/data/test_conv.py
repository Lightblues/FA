from flowagent.data import Conversation, Message, Role


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


test_message()
# test_add_message()
