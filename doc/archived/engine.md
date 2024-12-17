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
