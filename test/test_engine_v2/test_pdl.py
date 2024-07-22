# %%
import json
from engine_v2.pdl import PDL
from engine_v2.controller import PDLController
pdl = PDL.load_from_file("/work/huabu/data/v240628/huabu_refine01/000-114挂号.txt")
# pdl

# %%
# print all the infos
for k, v in pdl.__dict__.items():
    print(f"{k}: {json.dumps(v, ensure_ascii=False)}")
# %%
controller = PDLController(pdl)
print(controller.graph)
# %%
controller.check_validation('挂号操作')
# %%
controller.check_validation('科室校验')
# %%
controller.check_validation('医院校验')
controller.check_validation('挂号操作')
# %%
controller.check_validation('科室校验')
controller.check_validation('挂号操作')
# %%

while True:
    break
else:
    print("else")
# %%
for i in range(3):
    print(i)
    break
else:
    print("else")
# %%
from engine_v2.common import BaseLogger
logger = BaseLogger()
logger.log_to_stdout("hello", color='orange')
# %%
