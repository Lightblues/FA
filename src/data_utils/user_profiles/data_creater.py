import argparse
import re
from typing import List

from easonsi.llm.openai_client import OpenAIClient
from engine import LLM_CFG, BaseRole, Config, init_client
from tqdm import tqdm

from utils.jinja_templates import jinja_render


class ProfileCreater(BaseRole):
    llm: OpenAIClient = None
    cfg: Config = None
    # task_desc: dict = None

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.llm = init_client("gpt-4o")

    def create_profile(self, task: str, personas: List[str], task_desc: str) -> int:
        profiles = []
        print(f"processing the personas for task: {task}")
        for persona in tqdm(personas):
            prompt = jinja_render(
                "data_utils/persona_to_profile.jinja",
                Task_Description=task_desc,
                Persona=persona,
            )
            # print(prompt)
            # print('=' * 20 + ' conversation ' + '=' * 20)
            # print(conversation.to_str())
            llm_resp = self.llm.query_one(prompt)
            print("=" * 20 + " resp " + "=" * 20)
            print(llm_resp)
            # print(llm_resp)
            # transfer to number
            # find the four parts in the response
            user_details, user_needs, dialogue_style, interative_pattern = (
                "",
                "",
                "",
                "",
            )
            try:
                """
                dialogue_info_idx = llm_resp.find('2. User needs:')
                style_idx = llm_resp.find('3. Dialogue Style:')
                interative_pattern_idx = llm_resp.find('4. Interaction Patterns:')
                user_details = llm_resp[:dialogue_info_idx].strip()
                user_needs = llm_resp[dialogue_info_idx + len('2. User needs:'): style_idx].strip()
                dialogue_style = llm_resp[style_idx + len('3. Dialogue Style:'): interative_pattern_idx].strip()
                interative_pattern = llm_resp[interative_pattern_idx + len('4. Interaction Patterns:'): ].strip()
                """
                # extract each part of the user profile
                # each part starts with "k. xxxx:"
                split_resp = re.findall(r"\d\..*?:", llm_resp)
                assert len(split_resp) == 4
                split_idx = [(llm_resp.find(split), llm_resp.find(split) + len(split)) for split in split_resp]
                split_info = []
                for i in range(len(split_resp) - 1):
                    split_info.append(llm_resp[split_idx[i][1] : split_idx[i + 1][0]])
                split_info.append(llm_resp[split_idx[-1][1] :])
                user_details = split_info[0].strip()
                user_needs = split_info[1].strip()
                dialogue_style = split_info[2].strip()
                interative_pattern = split_info[3].strip()
            except Exception as e:
                print(f"error {e} when parsing llm response. llm response: ", llm_resp)

            user_profile = {
                "persona": persona,
                "user_details": user_details,
                "user_needs": user_needs,
                "dialogue_style": dialogue_style,
                "interative_pattern": interative_pattern,
            }
            print("=" * 20 + " profile " + "=" * 20)
            for key in user_profile:
                print(f"{key}:\n {user_profile[key]}\n")
            profiles.append(user_profile)
        return profiles


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="gpt-4o-mini")
    args = parser.parse_args()

    cfg = Config()
    if args.model_name:
        cfg.model_name = args.model_name

    creater = ProfileCreater(cfg=cfg)
