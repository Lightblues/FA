from flowagent.data import Config, DataManager, Conversation, Message, Role
from frontend.frontend_client import FrontendClient
import streamlit as st

client = FrontendClient()
conversation_id = "xxx"
cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
def main():
    conv = client.single_register(conversation_id, cfg)
    conv.add_message(Message(role=Role.USER, content="给我讲一个笑话吧", conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id))
    print("sent query...")
    
    # 使用 Streamlit 的 expander 显示流式输出
    with st.expander("Thinking...", expanded=True):
        stream = client.single_bot_predict(conversation_id, conv)
        # for chunk in stream:
        #     st.write(chunk)  # 或者使用 st.write_stream(chunk) 来流式显示
        #     print(chunk, end="")
        st.write_stream(stream)
    
    bot_output = client.single_bot_predict_output(conversation_id)
    print(f"> bot_output: {bot_output}")
    print()

if __name__ == '__main__':
    # asyncio.run(main())
    main()