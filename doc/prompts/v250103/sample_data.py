conversation = """ 
[BOT_MAIN] 你好，有什么可以帮您?
[USER] 挂301的口腔科
[BOT_MAIN] <Call workflow> 114挂号
[BOT_114挂号] <Call API> check_hospital_exist({'hos_name': '北京301医院'})
""".strip()
current_state = """
- current time: 2025-01-02 20:13:55 (Thursday)
- current user query: "挂301的口腔科"
""".strip()

conversation_Congo = """ [BOT] 你好，我是这个物品可以寄送吗机器人，有什么可以帮您?
[USER] 寄东西去刚果民主共和国 """.strip()
current_state_Congo = """
- current time: 2025-01-02 20:13:55 (Thursday)
- current user query: "寄东西去刚果民主共和国"
""".strip()
