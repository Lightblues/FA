from typing import Dict, List

from loguru import logger
from pydantic import BaseModel

from common import LLM_CFG, Config, Formater, OpenAIClient, init_client, jinja_render
from data import Conversation


class EntityLinker(BaseModel):
    """abstract of entity linking
    Variables:
        cfg. [api_entity_linking_llm, api_entity_linking_template]

    Used config:
        api_entity_linking_llm
        api_entity_linking_template

    Usage::
        entity_linker = EntityLinker(cfg=cfg, conv)
        res = entity_linker.entity_linking("朝阳医院", ['北京301医院', '北京安贞医院', '北京朝阳医院', '北京大学第一医院', '北京大学人民医院', '北京儿童医院', '北京积水潭医院', '北京世纪坛医院', '北京天坛医院', '北京协和医学院附属肿瘤医院', '北京协和医院', '北京宣武医院', '北京友谊医院', '北京中日友好医院', '北京中医药大学东方医院', '北京中医药大学东直门医院'])
    """

    cfg: Config = None
    llm: OpenAIClient

    def __init__(self, cfg: Config, conv: Conversation = None) -> None:
        self.cfg = cfg
        self.conv = conv
        self.llm = init_client(llm_cfg=LLM_CFG[cfg.api_entity_linking_llm])
        # print(f">> [api] init EL model `{cfg.api_entity_linking_llm}`")

    def entity_linking(self, query: str, eneity_list: List[str]) -> Dict:
        """Given a list of candidate entities, use llm to determine which one is most similor to the input
        return :
        """
        meta = {}

        # if DEBUG: print(f">> runing EL for {query} with {json.dumps(eneity_list, ensure_ascii=False)}")
        res = {"is_matched": True, "matched_entity": None}
        prompt = jinja_render(self.cfg.api_entity_linking_template, query=query, eneity_list=eneity_list)
        llm_response = self.llm.query_one(prompt)
        _debug_msg = f"\n{'[EL]'.center(50, '=')}\n<<prompt>>\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
        logger.bind(custom=True).debug(_debug_msg)
        meta.update(prompt=prompt, llm_response=llm_response)

        # todo: error handling
        parsed_response = Formater.parse_llm_output_json(llm_response)
        if parsed_response["is_matched"]:
            res["matched_entity"] = parsed_response["matched_entity"]
        else:
            res["is_matched"] = False
        return res, meta
