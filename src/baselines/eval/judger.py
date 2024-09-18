import re, yaml, tabulate
import pandas as pd
from typing import List, Dict, Optional, Tuple
from easonsi.llm.openai_client import OpenAIClient, Formater

from ..data import (
    Config,
    Workflow, DBManager, DataManager
)
from engine import (
    Role, Message, Conversation, ActionType, ConversationInfos, Logger, BaseLogger,
    LLM_CFG, init_client
)
from utils.jinja_templates import jinja_render


class Judger:
    cfg: Config = None
    db: DBManager = None
    logger: Logger = None
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.db = DBManager(cfg.db_uri, cfg.db_name, cfg.db_message_collection_name)
        self.logger = BaseLogger()

    def judge(self, verbose=True):
        """ judge process:
        1. check if judged
        2. collect related infos
        3. judge
        4. record the result
        """
        # 0. check if judged
        assert self.cfg.judge_conversation_id is not None, "judge_conversation_id is None"
        query = {
            "conversation_id": self.cfg.judge_conversation_id
        }
        query_res = self.db.query_evaluations(query)
        if len(query_res) > 0:
            self.logger.log(f"  <judge> {self.cfg.judge_conversation_id} has already been judged", with_print=verbose)
            return True

        # 1.1. get the simultead conversation
        simulated_conversation = self.db.query_messages_by_conversation_id(self.cfg.judge_conversation_id)
        assert len(simulated_conversation) > 0, "simulated conversation is empty"
        
        # 1.2. get the workflow infos
        data_manager = DataManager(self.cfg)
        workflow = Workflow.load_by_id(
            data_manager=data_manager,
            id=self.cfg.workflow_id, type=self.cfg.workflow_type,
            load_user_profiles=True
        )
        user_profile = workflow.user_profiles[self.cfg.user_profile_id]
        
        # 2. judge: call the judge model & parse the output
        self.logger.log(f"  <judge> start to judge {self.cfg.judge_conversation_id}", with_print=verbose)
        client = init_client(llm_cfg=LLM_CFG[self.cfg.judge_model_name])
        prompt = jinja_render(
            "baselines/eval_session.jinja",
            user_target=user_profile.to_str(),
            workflow_info=workflow.to_str(),
            session=simulated_conversation.to_str(),  # TODO: format the conversation
        )
        res, _model_name, _usage = client.query_one(prompt, return_usage=True)
        jr = self.parse_react_output(res)
        out = {
            "conversation_id": self.cfg.judge_conversation_id,
            "exp_version": self.cfg.exp_version,  # these infos can be found in `db.config`
            **{ k:v for k,v in self.cfg.to_dict().items() if k.startswith("workflow") },
            "judge_model": _model_name,
            "judge_usage": _usage,
            "judge_result": jr,
            # TODO: standardize the judge results
            "prompt": prompt,
            "llm_response": res,
        }
        # 2.2. save the judge result to db
        self.db.insert_evaluation(out)
        self.logger.log(f"  <judge> {self.cfg.judge_conversation_id} has been judged", with_print=verbose)
        return out
    
    @staticmethod
    def parse_react_output(s: str, slots:List[str] = ['Result', 'Total number of goals', 'Number of accomplished goals', 'Reason']):
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
        _slots = '|'.join(slots)    # Status Code|Data)
        pattern = f"(?P<field>{_slots}):\s*(?P<value>.*?)(?=\n({_slots}):|\Z)"
        matches = re.finditer(pattern, s, re.DOTALL)
        result = {match.group('field'): match.group('value').strip() for match in matches}
        # validate result
        assert all(key in result for key in slots), f"{slots} not all in prediction: {s}"
        return result
    
    def start_judge(self, verbose=True):
        infos = {
            "conversation_id": self.cfg.judge_conversation_id,
            "judge_model_name": self.cfg.judge_model_name,
            "exp_version": self.cfg.exp_version,
            **{ k:v for k,v in self.cfg.to_dict().items() if k.startswith("workflow") },
            "config": self.cfg.to_dict(),
        }
        infos_header = tabulate.tabulate(pd.DataFrame([infos]).T, tablefmt='psql', maxcolwidths=100)
        self.logger.log(infos_header, with_print=verbose)
        
        res = self.judge(verbose=verbose)
        
        infos_end = tabulate.tabulate(pd.DataFrame([res]).T, tablefmt='psql', maxcolwidths=100)
        self.logger.log(infos_end, with_print=verbose)
        return res