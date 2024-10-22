from typing import List
from ..base import BaseAPIHandler
from ...data import APIOutput, BotOutput, Role, Message

class DummyAPIHandler(BaseAPIHandler):
    """ 
    API structure: (see apis_v0/apis.json)
    """
    names: List[str] = ["dummy_api"]
    api_template_fn: str = ""
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.cnt_api_callings: int = 0
        
    def process(self, *args, **kwargs) -> APIOutput:
        """ 
        1. match and check the validity of API
        2. call the API (with retry?)
        3. parse the response
        """
        # raise NotImplementedError
        self.cnt_api_callings += 1
        
        self.conv.add_message(
            Message(role=Role.SYSTEM, content="api calling..."),
        )
        api_output = APIOutput()
        return api_output