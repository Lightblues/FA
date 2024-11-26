from flowagent.data import Conversation, Message, Role

def test_custom_role():
    msg = Message("user", "hello")
    print(msg, msg.role)

    msg = Message("custom_role", "hello")
    print(msg, msg.role)

test_custom_role()
print()
