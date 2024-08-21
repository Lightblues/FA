""" Collect simulated conversations.
output: https://docs.google.com/spreadsheets/d/1p36xAuhiv9siLo7Lw7bFGk9U33rBBKZOKUetYcLQQt4/edit?gid=1151625617#gid=1151625617
"""

# %%
import os, json, tqdm, itertools
import pandas as pd

from engine import _DIRECTORY_MANAGER
from easonsi import utils
from easonsi.files.gsheet import GSheet
gsheet = GSheet()

_ddir = _DIRECTORY_MANAGER.DIR_simulated_base / "template=query_PDL_jinja_pdl=pdl2_step3_model=qwen2_72B_api=llm"
fns = sorted(os.listdir(_ddir))


# %%
def parse_conv(conversation_s:str):
    convs = []
    utter = ""
    role, utterence = None, ""
    for line in conversation_s.split("\n"):
        if not line.strip(): continue
        if line.startswith("[BOT]"):
            if role == "user":
                convs.append(utterence)
                utterence = line
            else:
                if utterence: utterence += "\n"
                utterence += line
            role = "bot"
        elif line.startswith("[USER]"):
            if role == "bot": 
                convs.append(utterence)
                utterence = line
            else:
                if utterence: utterence += "\n"
                utterence += line
            role = "user"
        else:
            if utterence: utterence += "\n"
            utterence += line
    convs.append(utterence)
    return convs

parsed_data = []
for fn in fns:
    data = utils.LoadJsonl(_ddir / fn)
    print(f"{fn}: {len(data)}")
    for d in data:
        parsed_data.append((
            d["workflow_name"],
            d["user_profile"],
            *parse_conv(d["simulated_conversation"])
        ))

# %%
df = pd.DataFrame.from_records(parsed_data)
col_names = ["workflow_name", "user_profile", "B0"]
ll = (len(df.columns) - 3) // 2
col_names += itertools.chain.from_iterable([(f"U{i}", f"B{i}") for i in range(1, ll+1)])
df.columns = col_names
df

# %%
gsheet.to_gsheet(df, sheet_name="simulated_conversations")
# %%
""" 
打分标准：

- 未能遵循流程，且对话无法正确结束，包括：
- 死循环：陷入死循环导致对话无法结束；
- 其他：其他由于模型原因导致对话无法结束的情况。

- 未能遵循流程，但是能够正常结束对话，包括以下错误：
- 偏离流程：在用户进行流程外询问后，不能及时把用户引导回流程；
- 分支错误：仍然在流程中，但是进入了流程中的错误分支；
- 流程不全：进入的分支正确，但还没达到`ANSWER`节点就终止了对话；
- 其他：其他由于模型原因导致对话未能遵循流程的情况。

- 基本遵循流程，但是解决过程中存在可能导致响应用户过慢或执行出错的问题，包括以下错误：
- API重复调用：调用某个API且得到足够信息后，连续重复调用同一个API，这里“同一个”指的是API名字和传入的参数相同；
- 参数不全：在还未获取到某个参数实际值的时候，就调用尝试调用这个参数相关的API；
- 其他：其他由于模型原因可能导致响应用户过慢或执行出错的情况。

- 遵循流程，基本没有明显错误，但是在回复的灵活性、顺畅性还存在不足，具体包括：
- 未利用已有信息：在用户已经提供某个slot值的时候，冗余地向用户询问这个slot，或者是过多地确认某个slot的值；
- 用词生硬：模型在对话上下文中使用重复的用词语法，导致对话不够自然；
- 处理用户流程外需求能力不足：无法对用户在流程定义之外的需求做出灵活的响应；
- 其他：其他模型回复不流畅的情况。

- 遵循流程，能够灵活处理用户询问，回复自然、顺畅
"""