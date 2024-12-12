

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
