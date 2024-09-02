import datetime, json, socketio, os
from typing import Optional, Dict, Tuple, List

from .common import init_client, LLM_CFG, DEBUG
from .datamodel import Conversation, PDL, ConversationInfos, ActionType, Message, Role
from .datamodel import Config, BaseRole
from .typings import BotActionMeta, APICalling_Info
from utils.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater
from utils.tcloud.tcloud_utils import get_token, get_request_id, get_session_id


class BaseBot(BaseRole):
    cfg: Config = None
    names: List[str] = []                   # for convert name2role

    def __init__(self, cfg:Config) -> None:
        super().__init__()
        self.cfg = cfg
        
    def process(self, *args, **kwargs) -> Tuple[ActionType, BotActionMeta, Message]:
        """ 
        return:
        """
        raise NotImplementedError

class PDLBot(BaseBot):
    llm: OpenAIClient = None
    names = ["pdl", "PDLBot"]
    
    def __init__(self, cfg:Config) -> None:
        super().__init__(cfg=cfg)
        self.llm = init_client(llm_cfg=LLM_CFG[cfg.model_name])
        if DEBUG: print(f">> [bot] init PDL model {cfg.model_name} with {json.dumps(LLM_CFG[cfg.model_name], ensure_ascii=False)}")
    
    def process(self, conversation:Conversation, pdl:PDL, conversation_infos:Optional[ConversationInfos]=None, print_stream=True) -> Tuple[ActionType, BotActionMeta, Message]:
        """ 
        return:
            action_type: [ActionType.REQUEST, ActionType.ANSWER, ActionType.API]
            action_metas: Dict, return API parameters if action_type == ActionType.API
        TODO: error process
        """
        action_metas = BotActionMeta
        
        s_current_state = None
        user_additional_constraints = None
        if conversation_infos is not None:
            s_current_state = f"Previous action type: {conversation_infos.curr_action_type.actionname}. The number of user queries: {conversation_infos.num_user_query}."
            user_additional_constraints = conversation_infos.user_additional_constraints
        head_info = f"Current time: {datetime.datetime.now().strftime('%Y-%m-%d (%A) %H:%M:%S')}"
        prompt = jinja_render(
            self.cfg.template_fn,       # "query_PDL.jinja"
            head_info=head_info,
            conversation=conversation.to_str(), 
            PDL=pdl.to_str(),
            current_state=s_current_state,
            user_additional_constraints=user_additional_constraints,
        )
        if print_stream:
            llm_response = self.llm.query_one_stream(prompt)
        else:
            llm_response = self.llm.query_one(prompt)
        action_metas.input_details = prompt; action_metas.output_details = llm_response
        
        parsed_response = Formater.parse_llm_output_json(llm_response)
        
        # -> ActionType
        assert "action_type" in parsed_response, f"parsed_response: {parsed_response}"
        try:
            action_type = ActionType[parsed_response["action_type"]]
        except KeyError:
            raise ValueError(f"Unknown action_type: {parsed_response['action_type']}")
        # -> action_metas
        action_name, action_parameters, response = parsed_response.get("action_name", "DEFTAULT_ACTION"), parsed_response.get("action_parameters", {}), parsed_response.get("response", "DEFAULT_RESPONSE")
        if type(action_parameters)==str: 
            try:
                action_parameters = eval(action_parameters)      # FIXME: parse error | json.loads
            except Exception as e:
                print(f"Error in action_parameters: {action_parameters}")
        assert type(action_parameters)==dict, f"action_metas should be dict instead of: {type(action_parameters)} {action_parameters}"
        action_metas.apicalling_info = APICalling_Info(name=action_name, kwargs=action_parameters)
        
        # -> msg
        if action_type == ActionType.API:
            msg = Message(Role.BOT, f"<Call API> {action_name}({action_parameters})")        # bot_callapi_template
        else:
            msg = Message(Role.BOT, response)
        return action_type, action_metas, msg
    

class LKEBot(BaseBot):
    sio: socketio.SimpleClient = None
    session_id: str = None
    names = ["lke", "LKEBot"]
    
    def __init__(self, cfg:Config) -> None:
        super().__init__(cfg=cfg)
        self._get_tcloud_bot()
    
    def _get_tcloud_bot(self,
        secret_id:str=os.getenv("TENCENTCLOUD_SECRET_ID", ""),
        secret_key:str=os.getenv("TENCENTCLOUD_SECRET_KEY", ""),
        bot_app_key:str=os.getenv("TCLOUD_BOT_KEY", ""),
        visitor_biz_id:str=os.getenv("TCLOUD_VISITOR_BIZ_ID", ""),
        conn_type_api = 5,  # API 访客
        region = "ap-guangzhou",
        tencent_cloud_domain = "tencentcloudapi.com",
        scheme = "https",
        req_method = "POST",
    ):
        if not (secret_id and secret_key and bot_app_key and visitor_biz_id): raise ValueError("Please set TENCENTCLOUD_SECRET_ID, TENCENTCLOUD_SECRET_KEY, TCLOUD_BOT_KEY, and TCLOUD_VISITOR_BIZ_ID")
        secret = {
            "secret_id": secret_id,
            "secret_key": secret_key
        }
        http_profile = {
            "domain": tencent_cloud_domain,
            "scheme": scheme,
            "method": req_method
        }
        params = {
            "Type": conn_type_api,
            "BotAppKey": bot_app_key,
            "VisitorBizId": visitor_biz_id
        }
        token = get_token(secret, http_profile, region, params)     # 一次性的
        
        sio = socketio.SimpleClient()
        sio.connect(url="wss://wss.lke.cloud.tencent.com",
                    socketio_path="v1/qbot/chat/conn",
                    transports=["websocket"],
                    auth={"token": token})
        self.sio = sio
        self.session_id = get_session_id()
        return sio
    
    def _process_str(self, content:str, action_meta: BotActionMeta) -> str:
        request_id = get_request_id()
        req_data = {"request_id": request_id, "content": content, "session_id": self.session_id}
        self.sio.emit("send", {"payload": req_data})
        while True:
            event, data = self.sio.receive(timeout=50)  # NOTE: a small timeout maybe lead TLE!
            if event=="reply":
                if data["payload"]["is_from_self"]:
                    action_meta.input_details = data["payload"] # add input details
                else:
                    if not data["payload"]["is_final"]: continue
                    action_meta.output_details = data["payload"] # add output details
                    res = data["payload"]["content"]
                    if res.startswith("您好，您还在吗？"):      # skip the dummy message!!
                        print(f"  >> Dummy response: {res}")
                    else: break
            elif event=="error":
                print(f'  >> [ERROR] LKEBot:  event:{event}, data:{data}')
                res = str(data)
                break
        return res
    
    def process(self, conversation:Conversation, pdl:PDL, conversation_infos:Optional[ConversationInfos]=None, print_stream=True) -> Tuple[ActionType, BotActionMeta, Message]:
        action_metas = BotActionMeta()
        response = self._process_str(conversation.msgs[-1].content, action_metas)
        action_type = ActionType.ANSWER
        msg = Message(Role.BOT, response)
        return action_type, action_metas, msg


BOT_ANME2CLASS: Dict[str, BaseBot] = {}
for cls in BaseBot.__subclasses__():
    for name in cls.names:
        BOT_ANME2CLASS[name] = cls