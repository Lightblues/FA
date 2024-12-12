# 前后端分离

## 原本
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

## UI 
### single
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

## 修改思路
- Q: 如何去维护 conversation? 
    see `test/backend/test_ui_backend.py`
- Q: 如何去维护 session? (何时更新 session_id)
    - 通过 refresh_session() 来收集UI中的配置, 并初始化 session, see `src/frontend/page_single.py`
    - 通过 single_disconnect() 来清除 session; 
    - 在页面关闭时, 通过 JavaScript 来清除 session
- Q: 接口设计? 
    see `src/backend/client.py` 实现一个标准化的client来匹配逻辑
- Q: DB & log
    - log: 复用原本的 loguru 方案;

DB
- backend_single_sessions
    - `session_id, user, mode, conversation, config`
- backend_single_messages (need?)

### Backend
从 single 到 multi

1. `test_ui_backend_multi.py` 设计client功能实现 (如何使用), 反推 client 接口;
    ```python
    Client
        .multi_register(conversation_id, cfg)
        .multi_disconnect(conversation_id)
        .multi_user_input(conversation_id, user_input)

        .multi_bot_main_predict(conversation_id)
        .multi_bot_main_predict_output(conversation_id)
        .multi_tool_main(conversation_id, agent_main_output)
        .multi_bot_workflow_predict(conversation_id)
        .multi_bot_workflow_predict_output(conversation_id)
        .multi_post_control(conversation_id, bot_output)
        .multi_tool_workflow(conversation_id, bot_output)
    ```
2. 规范接口: `backend/` 中的 client/router/typings;
3. 对照 page_multi_workflow.py 实现逻辑, 重构 `Multi_Main_UIBot` 等组件;
4. 继续用 `test_ui_backend_multi.py` 来测试 client;

### Frontend
1. 参考已有的 multi-UI 交互逻辑, 搭建 `ui_multi.py`;
2. 梳理组件之间的逻辑, 实现 `data_multi.py`; 
    1. refresh_session, debug_print_infos


