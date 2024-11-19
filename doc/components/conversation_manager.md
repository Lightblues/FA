## ConversationManager

1. 原本的engine逻辑还算清晰 (虽然是不够完善的) 后面越来越冗杂; 这里抽象出最核心的会话逻辑
2. Bot 输出: 正如 FlowBench 里面参考 ReAct 格式定义了两类输出, 只处理 BotOutputType.RESPONSE/ACTION 两种类别! 
3. 终止逻辑: 只允许用户终止, bot负责响应即可. 

```python
class BaseConversationManager:
    cfg: Config = None
    user: BaseUser = None
    bot: BaseBot = None
    api: BaseAPIHandler = None
    logger: Logger = None
    conv: Conversation = None       # global variable for conversation
    
    def __init__(self, cfg:Config) -> None:
        self.conv = Conversation()
        self.user = USER_NAME2CLASS[cfg.user_mode](cfg=cfg, conv=self.conv)
        self.bot = BOT_NAME2CLASS[cfg.bot_mode](cfg=cfg, conv=self.conv)
        self.api = API_NAME2CLASS[cfg.api_mode](cfg=cfg, conv=self.conv)
        self.cfg = cfg
    
    def conversation(self, workflow: Workflow):
        """ 
        1. initiation: initialize the variables, logger, etc.
        2. main loop
            stop: by user (or bot?) -- only user!
            controller: 
                > bot can take several actions in one turn? 
        """
        # ...init, log meta infos
        role: Role = Role.USER      # current role!
        
        num_turns = 0
        while True:
            if role == Role.USER:
                user_output: UserOutput = self.user.process()
                # ...infos, log
                role = Role.BOT
            elif role == Role.BOT:
                num_bot_actions = 0
                while True:         # limit the bot prediction steps
                    bot_output: BotOutput = self.bot.process(...)
                    if bot_output.action_type == BotOutputType.RESPONSE:
                        break
                    elif bot_output.action_type == BotOutputType.ACTION:
                        # ... call the API, append results to conversation
                        api_output: APIOutput = self.api.process(bot_output.action, bot_output.action_input)
                    
                    num_bot_actions += 1
                    if num_bot_actions > self.cfg.bot_action_limit: 
                        # ... the default response
                        break
                role = Role.USER
            num_turns += 1
            if num_turns > self.cfg.conversation_turn_limit: break
        
        return self.conversation
```

### 交互逻辑

1. 命令行显示头尾信息; 
2. 中间是 u/b/s 的消息, 通过不同的颜色来区分; 

```sh
+----------+-------------------------------------------------------------------------------------------------------------------------------------+
| log_file | tmp.log                                                                                                                             |
| time     | 2024-09-05 11:25:30                                                                                                                 |
| config   | {'conversation_turn_limit': 10, 'user_mode': 'dummy_user', 'bot_mode': 'dummy_bot', 'bot_action_limit': 5, 'api_mode': 'dummy_api'} |
+----------+-------------------------------------------------------------------------------------------------------------------------------------+
[USER] user query...
[BOT] bot response...
[USER] user query...
[BOT] bot action...
[SYSTEM] api calling...
[BOT] bot response...
====================== END! ======================
```
