# code notes

## 数据存储 (mongo)

1. `conversation_id` 标记一个会话, 关联三张表
2. `exp_version` 标记一组实验, 一个exp_version中的实验包含相同的 workflow_dataset & workflow_type
    1. 因此, `exp_version + workflow_id + user_profile_id` 标记了一个实验中的一次实验
    2. 一个固定的 exp_version 关联其他的参数, fix 下来 (dump config). 

```sh
# config. PK: conversation_id
(exp_version, conversation_id), log_file, <config> (workflow_dataset, workflow_type, workflow_id), ...
# messages. PK: (conversation_id, utterance_id), FK: (conversation_id)
(conversation_id, utterance_id), (role, content), (prompt, llm_response)
# eval FK: (conversation_id)
(conversation_id), judje_model, <eval results>
```


## engine of PDL

### engine_v2

1. 简化了 v1 的代码结构
    1. 对于`User, APIHandler, Bot` 三个角色进行统一抽象, 通过 `process(...)` 函数来进行数据交互!
    2. 增加 `ConversationController` 来对于会话流程进行控制, 通过 `next_role(self, curr_role:Role, action_type)` 函数来获取下一个角色! 
    3. 从而将log逻辑统一放在外层会话中, 避免了bot内部进行log的调用! 


### engine_v1
<details>
<summary>engine_v1 实现了基本的抽象, 但整体流程代码框架比较脏. 后面直接重写了一版. </summary>

1. 从角色定义的角度, 定义了 `User, APIHandler, Bot` 三个角色, 分别以一定的数据需求来进行交互;
    1. 不同于 @ian 的面向过程的prompt处理 (见 ui 部分), 将整体控制逻辑整合在bot的处理流程中 —— 这样就需要将 logger, api_handler 放在bot类内部; 另外注意还有外部控制逻辑, 外部的conversation控制流程和bot内部的调用逻辑都需要进行log. 
2. 在数据层面, 定义 `Role, Message, Conversation`; 会话记录在交互过程中得以维护;
3. 具体来说, 
    1. APIHandler 根据需求实现了不同的版本; 
4. 关于日志系统, 简单将重要信息和LLM调用的详细信息分为两部分进行存储! 

```python
# see [engine_v1/datamodel]
class BaseUser:
    def generate(self, conversation:Conversation) -> Message:
        """ 根据当前的会话进度, 生成下一轮query """
class BaseAPIHandler:
    def process_query(self, conversation:Conversation, api_name: str, api_params: Dict) -> str:
        """ 给定上下文和当前的API请求, 返回API的响应 """
class BaseBot:
    api_handler: BaseAPIHandler = None      # 用于处理API请求
    def process(self, conversation:Conversation) -> str:
        """ 处理当前轮query """
```
</details>

## baselines (FlowBench)

### 框架: controller
1. 原本的engine逻辑还算清晰 (虽然是不够完善的) 后面越来越冗杂; 这里抽象出最核心的会话逻辑
2. Bot 输出: 正如 FlowBench 里面参考 ReAct 格式定义了两类输出, 只处理 BotOutputType.RESPONSE/ACTION 两种类别! 
3. 终止逻辑: 只允许用户终止, bot负责响应即可. 

```python
# baselines/main.py
class BaselineController:
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




## ui
采用 `streamlit` 包, ref [/apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/UI/v2.1]

### data (`st.session_state`)

- 首先在 [init_sidebar()] 中初始化:
    - 配置参数: `model_name, template_fn, workflow_dir, worflow_name` 前两者定义模型, 后两者定义当前画布
    - `pdl`: 当前画布
- 然后在 [init_agents()] 中进行其他变量初始化:
    - `infos` 记录当前会话的相关信息
    - `logger` 日志
    - `client, api_handler, bot` 

### framework: streamlit

1. 相较于 engine_v1, 重要的参数均在一开始的时候放到 `session_state` 中! (更准确地说, 是需要操控的参数, 其他的数据应该用cache即可), **这应该也是streamlit框架的使用方式**? —— 前者将重要参数放在主类中封装, 后者放在会话状态中! 
2. 这样造成的一个重要改动, 在ui中, bot的相关控制逻辑转移到了 `main()` 中, 在代码的控制结构上造成了一定的复杂性... 从面向对象的编程转为面向过程. 

