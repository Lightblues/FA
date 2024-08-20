""" 
统计PDL prompt的长度
"""

# %%
import tiktoken, os, sys, yaml, datetime
from transformers import AutoTokenizer, AutoModelForCausalLM, PreTrainedTokenizer
import numpy as np
from utils.jinja_templates import jinja_render
from engine import (
    _DIRECTORY_MANAGER, PDL, PDL_v2
)

# %%
def stat_prompt_len(tokenizer):
    token_lengths = []
    for fn in sorted(os.listdir(_DIRECTORY_MANAGER.DIR_huabu_step3)):
        pdl = PDL.load_from_file(_DIRECTORY_MANAGER.DIR_huabu_step3 / fn)
        token_length = len(tokenizer.encode(pdl.PDL_str))
        token_lengths.append(token_length)
    print(f"Avg token length of PDL_v1: {np.mean(token_lengths)}")

    token_lengths = []
    for fn in sorted(os.listdir(_DIRECTORY_MANAGER.DIR_data_base / "pdl2_0729")):
        pdl = PDL_v2.load_from_file(_DIRECTORY_MANAGER.DIR_data_base / "pdl2_0729" / fn)
        token_length = len(tokenizer.encode(pdl.PDL_str))
        token_lengths.append(token_length)
    print(f"Avg token length of PDL_v2: {np.mean(token_lengths)}")

    token_lengths_full = []
    head_info = f"Current time: {datetime.datetime.now().strftime('%Y-%m-%d (%A) %H:%M:%S')}"
    for fn in sorted(os.listdir(_DIRECTORY_MANAGER.DIR_huabu_step3)):
        pdl = PDL.load_from_file(_DIRECTORY_MANAGER.DIR_huabu_step3 / fn)
        prompt = jinja_render(
            "query_PDL.jinja",
            head_info=head_info,
            conversation="xxx", 
            PDL=pdl.PDL_str,
            current_state="xxx"
        )
        token_lengths_full.append(len(tokenizer.encode(prompt)))
    print(f"Avg token length of full prompt: {np.mean(token_lengths_full)}")

# %%
""" 发现qwen的中文编码效率还是要高出openai不少的!
## OpenAI
Avg token length of PDL_v1: 768.8846153846154
Avg token length of PDL_v2: 373.6923076923077
Avg token length of full prompt: 1215.8846153846155
## Qwen2
Avg token length of PDL_v1: 593.3461538461538
Avg token length of PDL_v2: 374.38461538461536
Avg token length of full prompt: 1041.3461538461538
"""
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")  # or "gpt-4", etc.
stat_prompt_len(encoding)

# %%
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-72B")
stat_prompt_len(tokenizer)

# %%
