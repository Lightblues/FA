"""数据生成全流程. (需要原始数据: apis, NL/PDL format workflow, seed persona)
1. convert API
2. build "task_infos.json"
3. convert formats
    PDL -> NL
    NL -> other formats
4. user profiles
"""

import json
import os
import pathlib
import random
import re

import tqdm
import yaml
from easonsi import utils
from easonsi.llm.openai_client import Formater
from engine import LLM_CFG, init_client

from data_utils.workflow_format.format_transformer import (
    FormatTransformer,
)
from utils.jinja_templates import jinja_render


IDIR = pathlib.Path("/work/huabu/dataset/_PDL_zh")
ODIR = pathlib.Path("/work/huabu/dataset/PDL")
os.makedirs(ODIR, exist_ok=True)

KEYS = [f"{i:03d}" for i in range(6)]
llm = init_client(llm_cfg=LLM_CFG["gpt-4o"])


format_to_codeblock = {
    "PDL": "PDL",
    "code": "python",
    "CoRE": "CoRE",
    "flowchart": "mermaid",
}
format_to_suffix = {"PDL": "txt", "code": "py", "CoRE": "txt", "flowchart": "md"}


class DataConverter:
    def __init__(self) -> None:
        # load meta data
        with open(ODIR / "task_infos.json", "r", encoding="utf-8") as f:
            self.task_infos = json.load(f)["task_infos"]
        api_infos = {}
        for task in KEYS:
            with open(ODIR / f"tools/{task}.yaml", "r", encoding="utf-8") as f:
                apis = yaml.load(f, Loader=yaml.FullLoader)
            api_infos[task] = apis
        self.api_infos = api_infos

    def transform_NL_to_other_format(self, target_format):
        """
        see src/data_utils/workflow_format/transform_format.py
        """
        NL_transformer = FormatTransformer(
            "gpt-4o",
            f"data_utils/NL_to_{target_format}.jinja",
            return_format=format_to_codeblock[target_format],
        )
        for task in tqdm.tqdm(KEYS):
            transformed_workflow = NL_transformer.transform(NL_desc=self.task_infos[task], apis=self.api_infos[task])
            file_suffix = format_to_suffix[target_format]
            os.makedirs(ODIR / f"{target_format}", exist_ok=True)
            with open(ODIR / f"{target_format}/{task}.{file_suffix}", "w", encoding="utf-8") as f:
                f.write(transformed_workflow)

    def translate_to_en_meta(self):
        os.makedirs(IDIR / "_text_en", exist_ok=True)
        for key in tqdm.tqdm(KEYS):
            with open(IDIR / "_text_zh" / f"{key}.json", "r", encoding="utf-8") as f:
                text = f.read()
            prompt = f"将下面的api列表翻译成英文, 保留格式\n```\n{text}\n```"
            llm_resp = llm.query_one(prompt)
            res = Formater.parse_codeblock(llm_resp, type="")
            with open(IDIR / "_text_en" / f"{key}.json", "w", encoding="utf-8") as f:
                f.write(res)

    def build_task_infos(self, version="v240908", subdir="_text_en"):
        task_infos = {}

        os.makedirs(ODIR / "text", exist_ok=True)
        for name in KEYS:
            with open(IDIR / subdir / f"{name}.json", "r") as f:
                task_info = json.load(f)
            task_infos[name] = {
                "name": task_info["task_name"],
                "task_description": task_info["task_description"],  # task_description
                "task_detailed_description": task_info["task_detailed_description"],
            }
            with open(ODIR / "text" / f"{name}.txt", "w") as f:
                f.write(task_info["task_detailed_description"])
        result = {"version": version, "task_infos": task_infos}
        with open(ODIR / "task_infos.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        return task_infos

    def create_user_profiles(self, task_desc, personas):
        """
        see src/data_utils/user_profiles/create_profile.py
        """
        profiles = []
        for persona in tqdm.tqdm(personas):
            prompt = jinja_render(
                "data_utils/persona_to_profile2.jinja",
                Task_Description=task_desc,
                Persona=persona,
            )
            llm_resp = llm.query_one(prompt)
            split_resp = re.findall(r"\d\..*?:", llm_resp)
            assert len(split_resp) == 5
            split_idx = [(llm_resp.find(split), llm_resp.find(split) + len(split)) for split in split_resp]
            split_info = []
            for i in range(len(split_resp) - 1):
                split_info.append(llm_resp[split_idx[i][1] : split_idx[i + 1][0]])
            split_info.append(llm_resp[split_idx[-1][1] :])
            user_details = split_info[0].strip()
            user_needs = split_info[1].strip()
            _apis = split_info[2].strip()
            _apis = _apis.split(",")
            required_apis = [api.strip() for api in _apis]
            dialogue_style = split_info[3].strip()
            interactive_pattern = split_info[4].strip()

            user_profile = {
                "persona": persona,
                "user_details": user_details,
                "user_needs": user_needs,
                "required_apis": required_apis,
                "dialogue_style": dialogue_style,
                "interactive_pattern": interactive_pattern,
            }
            profiles.append(user_profile)
        return profiles

    def create_user_profiles_for_all_tasks(self):
        fn_persona = "/apdcephfs_cq8/share_2992827/shennong_5/siqiicai/data/persona-hub/persona_expanded.jsonl"
        personas = utils.LoadJsonl(fn_persona)
        personas = [p["persona"] for p in personas]

        os.makedirs(ODIR / "user_profile", exist_ok=True)
        for task in KEYS:
            ofn = ODIR / f"user_profile/{task}.json"
            if ofn.exists():
                continue

            task_desc_str = "\n".join(f"{k}: {v}" for k, v in self.task_infos[task].items())

            task_desc_str += "\n\nAPIs: " + yaml.dump(self.api_infos[task], indent=2, allow_unicode=True)
            selected_personas = random.sample(personas, 15)

            print(f"processing the personas for task: {task}")
            profiles = self.create_user_profiles(task_desc_str, selected_personas)

            with open(ofn, "w") as f:
                json.dump(profiles, f, indent=2, ensure_ascii=False)

    def pdl_to_NL(subdir="pdl"):
        print(f"Converting NL from `{subdir}` subfolder")
        os.makedirs(ODIR / "_text", exist_ok=True)
        for name in tqdm.tqdm(KEYS):
            _ofn = ODIR / "_text" / f"{name}.json"
            if os.path.exists(_ofn):
                continue

            with open(IDIR / subdir / f"{name}.yaml", "r") as f:
                pdl = f.read()

            prompt = jinja_render("data_utils/pseudo_to_NL.jinja", pseudo=pdl)
            llm_resp = llm.query_one(prompt)
            res = Formater.parse_llm_output_json(llm_resp)
            with open(_ofn, "w") as f:
                json.dump(res, f, indent=2, ensure_ascii=False)

    def convert_format_api(subdir="api_v02/api_schemas"):
        print(f"Converting api from `{subdir}` subfolder")
        os.makedirs(ODIR / "tools", exist_ok=True)
        num_success = 0
        for name in tqdm.tqdm(KEYS):
            _ofn = ODIR / "tools" / f"{KEYS}.yaml"
            if os.path.exists(_ofn):
                continue

            with open(IDIR / subdir / f"{name}.json", "r") as f:
                data = json.load(f)
            prompt = jinja_render("data_utils/transform_api_format.jinja", API=json.dumps(data, indent=2))
            llm_resp = llm.query_one(prompt)
            converted_api = Formater.parse_llm_output_json(llm_resp)

            with open(_ofn, "w") as f:
                yaml.dump(converted_api, f, indent=2, allow_unicode=True, sort_keys=False)
        return num_success

    def translate_PDL_to_en(self):
        os.makedirs(ODIR / "pdl", exist_ok=True)
        for key in tqdm.tqdm(KEYS):
            with open(IDIR / "pdl" / f"{key}.yaml", "r", encoding="utf-8") as f:
                text = f.read()
            prompt = jinja_render("data_utils/translate_PDL.jinja", pdl=text, api=self.api_infos[key])
            llm_resp = llm.query_one(prompt)
            res = Formater.parse_codeblock(llm_resp, type="yaml")
            with open(ODIR / "pdl" / f"{key}.yaml", "w", encoding="utf-8") as f:
                f.write(res)


converter = DataConverter()
# converter.translate_to_en_meta()
# converter.build_task_infos()
# converter.transform_NL_to_other_format("code")
# converter.transform_NL_to_other_format("flowchart")
# converter.create_user_profiles_for_all_tasks()
converter.translate_PDL_to_en()
