""" updated @240918

- [ ] add "Tool Invocation" metrics in FlowBench
"""

import re, yaml, tabulate
import pandas as pd
from typing import List, Dict, Optional, Tuple
from easonsi.llm.openai_client import OpenAIClient, Formater

from ..data import (
    Config,
    Workflow, DBManager, DataManager, UserProfile
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

        out_dict = {
            "conversation_id": self.cfg.judge_conversation_id,
            "exp_version": self.cfg.exp_version,  # these infos can also be found in `db.config`
            **{ k:v for k,v in self.cfg.to_dict().items() if k.startswith("workflow") },

            "num_turns": len(simulated_conversation),       # //2
        }
        # NOTE: standardize the judge results
        # output format: `judge_session_result, judge_session_stat`
        _judge_session_res = self._judge_session(user_profile, workflow, simulated_conversation)
        _judge_session_stat_res = self._judge_stat_session(user_profile, simulated_conversation)
        # out_dict.update(_judge_session_res); out_dict.update(_judge_session_stat_res)
        out_dict |= _judge_session_res | _judge_session_stat_res
        
        # 2.2. save the judge result to db
        self.db.insert_evaluation(out_dict)
        self.logger.log(f"  <judge> {self.cfg.judge_conversation_id} has been judged", with_print=verbose)
        return out_dict
    
    def _judge_session(
        self, user_profile: UserProfile, workflow: Workflow, simulated_conversation: Conversation,
        retry:int=3
    ) -> Dict[str, str]:
        """ 
        output format:
            judge_session_result: Dict of results
            judge_session_details: Dict of detailed infos
        """
        client = init_client(llm_cfg=LLM_CFG[self.cfg.judge_model_name])
        prompt = jinja_render(
            "baselines/eval_session.jinja",
            user_target=user_profile.to_str(),
            workflow_info=workflow.to_str(),
            session=simulated_conversation.to_str(),  # TODO: format the conversation
        )
        for _retry in range(retry):
            try:
                res, _model_name, _usage = client.query_one(prompt, return_usage=True)
                jr = self._parse_react_output(res)
                break
            except Exception as e:
                self.logger.log(f"  <judge> error: {e}", with_print=True)
        else:
            raise Exception(f"  <judge> failed to judge for {retry} times!!! Prompt: \n{prompt}")
        
        return {
            "judge_session_result": jr,
            "judge_session_details": {
                "model": _model_name,   # judge model & detailed infos
                "usage": _usage,
                "prompt": prompt,
                "llm_response": res,
            }
        }
    
    def _judge_stat_session(self, user_profile: UserProfile, simulated_conversation: Conversation):
        apis_gt = user_profile.required_apis
        assert apis_gt is not None, "user_profile.required_apis is None"
        # stat called apis. 
        apis_pred = simulated_conversation.get_called_apis()
        return {
            "judge_session_stat": {
                "apis_gt": apis_gt,
                "apis_pred": apis_pred
            }
        }
    
    @staticmethod
    def _parse_react_output(s: str, slots:List[str] = ['Result', 'Total number of goals', 'Number of accomplished goals', 'Reason']):
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