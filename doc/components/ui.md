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
