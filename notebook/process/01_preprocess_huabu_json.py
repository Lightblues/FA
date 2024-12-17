"""
预处理所给的xlsx形式的画布数据
- 去除错误数据
- 规范文件名
"""

# %%
import json
import os

import pandas as pd
from tqdm import tqdm


DIR_data = f"../../data/画布json-v240627"

# %%
df_raw = pd.read_excel(f"{DIR_data}/taskflow-1.xlsx", header=None)
df_raw.head()

# %%
# keep only the first 3 columns, named [id, name, json]
df = df_raw.iloc[:, :3]
df.columns = ["id", "name", "json"]
df.head()
# %%
json.loads(df.iloc[0, 2])


# %%
def f_filter(s):
    try:
        res = json.loads(s)
        return True
    except Exception as e:
        return False


df_filtered = df[df["json"].apply(f_filter)]
print(f"#samples: {len(df)}, #filtered: {len(df_filtered)}")

# %%
DIR_output = f"{DIR_data}/json_step0"
os.makedirs(DIR_output, exist_ok=True)
for i, row in tqdm(df_filtered.iterrows()):
    fn = f"{i:03d}-{str(row['name']).replace('/', '_')[:10]}.json"  # 避免文件名过长, 不合法
    with open(f"{DIR_output}/{fn}", "w") as f:
        f.write(json.dumps(json.loads(row["json"]), indent=4, ensure_ascii=False))


# %%
""" ================================================================
"""
import json
import os

import pandas as pd
from tqdm import tqdm


DIR_data = f"../../data/v240628"
df_raw = pd.read_csv(f"{DIR_data}/db_llm_robot_task_sql_result_20240628144836.csv")
df_raw.head()
# %%
DIR_output = f"{DIR_data}/huabu_step0"
os.makedirs(DIR_output, exist_ok=True)
for i, row in tqdm(df_raw.iterrows()):
    fn = f"{i:03d}-{str(row['f_intent_name']).replace('/', '_')[:10]}.json"  # 避免文件名过长, 不合法
    with open(f"{DIR_output}/{fn}", "w") as f:
        f.write(json.dumps(json.loads(row["f_dialog_json_enable"]), indent=4, ensure_ascii=False))

# %%
