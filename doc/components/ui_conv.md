
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

