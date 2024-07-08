from engine_v1.datamodel import Conversation, Role

conversation = Conversation()
conversation.add_message(Role.USER, "Hello")
conversation.add_message(Role.BOT, "Hi")
print(conversation.to_str())