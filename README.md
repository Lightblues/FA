## TODOs

data
- [x] LLM auto generate node dependencies #2 @0724
- [x] LLM-based PDL generation @0729

functionalities
- [x] Auto evaluation: `user, api` agent @240716
- [x] implement an UI for interaction @240718
    - [x] move the engine_v2
- [x] PDL controllable/dependency execuation #1 @240722 [engine_v2]
    - [ ] add dependency for ANSWER nodes
- [ ] UI
    - [x] add additional user instructions in UI
    - [x] add session-ID in UI; add user-ID in log
    - [x] add config: set the shown models and PDLs and tempaltes @240821
- [ ] bot memory  https://github.com/mem0ai/mem0

APIs
- [x] When pass "--api_mode=vanilla", select and start the API server automatically @240718
- [ ] Generate API data automatically? #3 
- [x] implement API exec by actual API calling #1  @0723
- [x] add entity linking! #2

prompting
- [ ] add summary/memory #2
- [x] add datetime @0729

paper
- [ ] auto conversation simulation (user agent) #1
- [ ] auto conversation evaluation (based on specific PDL) #1

bugs
- [ ] fix `Current state` info -- action type and # user query
- [x] fix: entity linking result write back to Message  #1 @240821
- [x] V2: remove `REQUEST` type @240821

## run

相关路径
- huabu PDL: `data/v240628/huabu_step3`
- conversation logs: `data/v240628/engine_v1_log/<data>/<time>.log`
- prompts: `src/utils/templates`

```sh
PROJECT_PATH=/apdcephfs_cq8/share_2992827/shennong_5/easonsshi/huabu
cd ${PROJECT_PATH}/src

# 运行交互, 在交互的时候参见 huabu PDL 数据
python main.py --model_name qwen2_72B --api_mode manual --template_fn query_PDL_v01.jinja --workflow_name 005  # workflow_name 即画布名称/ID, 见 huabu PDL 路径
```

## code

### engine_v1

#### structure
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


### ui
采用 `streamlit` 包, see [/apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/UI/v2.1]

#### data (`st.session_state`)
- 首先在 [init_sidebar()] 中初始化:
    - 配置参数: `model_name, template_fn, workflow_dir, worflow_name` 前两者定义模型, 后两者定义当前画布
    - `pdl`: 当前画布
- 然后在 [init_agents()] 中进行其他变量初始化:
    - `infos` 记录当前会话的相关信息
    - `logger` 日志
    - `client, api_handler, bot` 

#### framework: streamlit
1. 相较于 engine_v1, 重要的参数均在一开始的时候放到 `session_state` 中! (更准确地说, 是需要操控的参数, 其他的数据应该用cache即可), **这应该也是streamlit框架的使用方式**? —— 前者将重要参数放在主类中封装, 后者放在会话状态中! 
2. 这样造成的一个重要改动, 在ui中, bot的相关控制逻辑转移到了 `main()` 中, 在代码的控制结构上造成了一定的复杂性... 从面向对象的编程转为面向过程. 

### engine_v2

1. 简化了 v1 的代码结构
    1. 对于`User, APIHandler, Bot` 三个角色进行统一抽象, 通过 `process(...)` 函数来进行数据交互!
    2. 增加 `ConversationController` 来对于会话流程进行控制, 通过 `next_role(self, curr_role:Role, action_type)` 函数来获取下一个角色! 
    3. 从而将log逻辑统一放在外层会话中, 避免了bot内部进行log的调用! 