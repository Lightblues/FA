
## base 
- [ ] change to `ctx` setting like MetaGPT?

```python
class BaseRole:
    names: List[str] = None         # for convert name2role
    cfg: Config = None              # unified config
    llm: OpenAIClient = None        # for simulation
    conv: Conversation = None       # global variable for conversation
    workflow: Workflow = None
```



## Bot

```python
class ReactBot(BaseBot):
    """ ReactBot
    prediction format: 
        (Thought, Response) for response node
        (Thought, Action, Action Input) for call api node
    """
    llm: OpenAIClient = None
    bot_template_fn: str = "flowagent/bot_flowbench.jinja"  # using the prompt from FlowBench
    names = ["ReactBot", "react_bot"]

    def process(self, *args, **kwargs) -> BotOutput:

class BotOutput:
    thought: str = None
    action: str = None                      # api name
    action_input: Dict = None               # api paras
    response: str = None
    @property
    def action_type(self) -> BotOutputType:

class BotOutputType(Enum):
    RESPONSE = ("RESPONSE", "response to the user")
    ACTION = ("ACTION", "call an API")
    END = ("END", "end the conversation")
```
