```python
# https://platform.openai.com/docs/guides/function-calling#if-the-model-generated-a-function-call
# name, arguments
class BotOutput:
    action: str = None                      # api name
    action_input: Dict = None               # api paras
```
