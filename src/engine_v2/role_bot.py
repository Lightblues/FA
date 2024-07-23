
from .common import init_client, LLM_CFG
from .datamodel import Conversation, PDL, ConversationInfos, ActionType, Message, Role
from .datamodel import Config, BaseRole
from utils.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater


class PDLBot(BaseRole):
    llm: OpenAIClient = None
    cfg: Config = None
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.llm = init_client(llm_cfg=LLM_CFG[cfg.model_name])
    
    def process(self, conversation:Conversation, pdl:PDL, conversation_infos:ConversationInfos=None, print_stream=True):
        """ 
        return:
            action_type: [ActionType.REQUEST, ActionType.ANSWER, ActionType.API]
            action_metas: Dict, return API parameters if action_type == ActionType.API
        """
        action_metas = {}
        
        if conversation_infos is not None:
            s_current_state = f"Previous action type: {conversation_infos.previous_action_type}. The number of user queries: {conversation_infos.num_user_query}."
        else:
            s_current_state = None
        prompt = jinja_render(
            self.cfg.template_fn,       # "query_PDL.jinja"
            conversation=conversation.to_str(), 
            PDL=pdl.to_str(),
            current_state=s_current_state
        )
        if print_stream:
            llm_response = self.llm.query_one_stream(prompt)
        else:
            llm_response = self.llm.query_one(prompt)
        action_metas.update(prompt=prompt, llm_response=llm_response)       # for debug
        # _debug_msg = f"{'[BOT]'.center(50, '=')}\n<<prompt>>\n{prompt}\n\n<<response>>\n{llm_response}\n"
        # self.logger.debug(_debug_msg)
        
        parsed_response = Formater.parse_llm_output_json(llm_response)
        
        # -> ActionType
        assert "action_type" in parsed_response, f"parsed_response: {parsed_response}"
        try:
            action_type = ActionType[parsed_response["action_type"]]
        except KeyError:
            raise ValueError(f"Unknown action_type: {parsed_response['action_type']}")
        # -> action_metas
        action_name, action_parameters, response = parsed_response.get("action_name", "DEFTAULT_ACTION"), parsed_response.get("action_parameters", "DEFAULT_PARAS"), parsed_response.get("response", "DEFAULT_RESPONSE")
        action_metas.update(action_name=action_name, action_parameters=action_parameters, response=response)
        
        # -> msg
        if action_type == ActionType.API:
            msg = Message(Role.BOT, f"<Call API> {action_name}({action_parameters})")        # bot_callapi_template
        else:
            msg = Message(Role.BOT, response)
        return action_type, action_metas, msg