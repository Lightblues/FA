## 前后端分离

### 原本那块
前端: streamlit
```python
# app.py | general
ss.logger
ss.conv
ss.data_manager: DataManager
ss.cfg: Config
ss.mode: "single" | "multi"
ss.headers: st.context.headers
ss.user_identity: Dict
ss.db: mongodb.Database

# page_single_workflow.py
ss.tool
ss.bot: PDL_UIBot
    .process_stream()
    .process_LLM_response(prompt, llm_response)
ss.controllers
ss.workflow
```

Bot
```python
# 原本的依赖
class PDL_UIBot():
    ss.cfg: ui_bot_llm_name | ui_bot_template_fn
    ss.workflow: pdl.status_for_prompt | pdl.to_str_wo_api() | toolbox
    ss.conv: .to_str()
    ss.user_additional_constraints
# 使用 (logger 放到后端)
@retry_wrapper(retry=3, step_name="step_bot_prediction", log_fn=ss.logger.bind(custom=True).error)
def step_bot_prediction() -> BotOutput:
    prompt, stream = bot.process_stream()
    bot_output = bot.process_LLM_response(prompt, llm_response)

# 修改后
def step_bot_prediction() -> StreamingResponse:
    stream = bot.process_stream()
    return bot.process_LLM_response(prompt, llm_response)
```

### 修改后
- Q: 如何去维护 conversation? 
    see `test/backend/test_ui_backend.py`
- Q: 如何去维护 session? (何时更新 session_id)
    通过 refresh_session() 来收集UI中的配置, 并初始化 session

UI of single
- 选择模型
- 选择模板
- 选择数据集
- 选择画布版本
- 选择画布
- 重置对话: `refresh_session`
- DEBUG: 后台打印相关信息. 
- 自定义配置
- 勾选使用的 workflows
- 查看 PDL / template
- 日志: sessionid / name




## multi_workflow
```python
# pesudo-code of main loop
def get_main_agent()
def get_workflow_agent()

def case_main():
    res = agent_main.process()  # stream process
    if res.workflow:
        status = "workflow"
        case_workflow()
    else: show_message(res.message)
def case_workflow():
    res = agent_workflow.process()
    if res.main:
        status = "main"
        case_main()
    else: show_message(res.message)

def main():
    status = "main"
    while True:
        user_input()
        if status=="main": case_main()
        else: case_workflow()
```

UI
1. 配置项: 选择模型/模板/数据版本/数据
2. 按钮: 重置对话
3. 输入: 自定义配置
4. 勾选: 使用的 workflows
5. 查看: PDL / template?
6. 日志: sessionid / name


## single_workflow
```python
    """ 
    交互逻辑: 
        当用户输入query之后, 用一个while循环来执行ANSWER或者API调用:
            用一个 expander 来展示stream输出
            若为API调用, 则进一步展示中间结果
        最后, 统一展示给用户的回复
        NOTE: 用 container 包裹的部分会在下一轮 query 后被覆盖
    日志:
        summary: 类似conversation交互, 可以增加必要信息
        detailed: 记录设计到LLM的详细信息
    """
```


UI
1. 配置项: 选择模型/模板/数据版本/数据
2. 按钮: 重置对话
3. 输入: 自定义配置
4. 勾选: controllers
5. 查看: PDL / template
6. 日志: sessionid / name
