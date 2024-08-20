
# %%
import json

from engine.user_profile import UserProfile
with open('/apdcephfs_cq8/share_2992827/shennong_5/siqiicai/jobs/huabu_test/huabu/data/gen/user_profile/profiles.json', 'r', encoding='utf-8') as f:
    profiles = json.load(f)
profile = UserProfile.load_from_dict(profiles['114挂号'][0])
print(profile.to_str())

# %%
from engine import LLMSimulatedUserWithProfile, PDL, Config, Conversation
cfg = Config.from_yaml("/work/huabu/src/configs/simulate.yaml")
pdl = PDL.load_from_file("/work/huabu/data/v240820/pdl2_step3/000-114挂号.yaml")
user = LLMSimulatedUserWithProfile(cfg=cfg, user_profile=profile)
conv = Conversation()
t, action_metas, msg = user.process(conversation=conv, pdl=pdl)

# %%
