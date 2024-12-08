## TODOs

- [ ] 实现工具: 现有画布转换, JSON -> PDL [可行性]
    - [ ] 需要兼容新的节点定义 [待验证]
- [ ] 验证在更大画布上的流程遵循稳定性
    - [x] 在新版本模型 (0.9.2) 上的效果测试
- [x] 探究多画布上的协作问题 & 通用插件的调用能力 [方案1] swarm 方案 #P1
- [ ] 调研 MetaGPT/Coze 中 multi-agent 的通信方式
- [ ] 前后端分离, 支持批量测试
- [ ] 数据构造, 支持模型训练 (DPO 量化后效果下降?)
- [ ] log & debug -> (page_inspect.py)
- [ ] 语法优化
    - [ ] API_check_hospital_exist -> `API.check_hospital_exist`

misc
- [x] 合并 aget-pdl & master 分支 #P2 (part 1)
- [ ] 标准化数据处理模块 (JSON -> PDL 的转换)
- [ ] 合并数据存储
- [x] UI: 此前的功能实现: 自定义配置

buds
- [ ] 点击 "重置对话", DAG controller 状态没有更新. 

see detailed in [feishu](https://v0r8x11vrv.feishu.cn/docx/WaMfdTbqaoH1WTx9ZDicVAB7nM9)

data

- [x] LLM auto generate node dependencies #2 @0724
- [x] LLM-based PDL generation @0729
- [x] auto conversation simulation (user agent) #1
- [x] auto conversation evaluation (based on specific PDL) #1
- [ ] auto PDL generation (with user query) [data source: wikihow] #P0

functionalities

- [x] Auto evaluation: `user, api` agent @240716
- [x] implement an UI for interaction @240718
    - [x] move the engine_v2
- [x] PDL controllable/dependency execuation #1 @240722 [engine_v2]
    - [ ] add dependency for ANSWER nodes
- [ ] UI
    - [x] add additional user instructions in UI
    - [x] add session-ID in UI; add user-ID in log
    - [x] add config: set the shown models and PDLs and tempaltes @240821
- [ ] bot memory  <https://github.com/mem0ai/mem0>

APIs

- [x] When pass "--api_mode=vanilla", select and start the API server automatically @240718
- [x] Generate API data automatically? #3 
- [x] implement API exec by actual API calling #1  @0723
- [x] add entity linking! #2
- [x] fix api params phase ERROR! #P0 @0830

prompting

- [ ] add summary/memory #2
- [x] add datetime @0729

baselines

- [x] FlowBench 
- [x] CoRE

bugs

- [x] fix `Current state` info -- action type and # user query
- [x] fix: entity linking result write back to Message  #1 @240821
- [x] V2: remove `REQUEST` type @240821

## run

```sh
PROJECT_PATH=/apdcephfs_cq8/share_2992827/shennong_5/easonsshi/huabu
cd ${PROJECT_PATH}/src

python run_flowagent_cli.py --mode=conv \
    --config=default.yaml --exp-version=default --exp-mode=turn \
    --workflow-type=text --workflow-id=000 \
    --user-mode=llm_profile --user-llm-name=gpt-4o --user-profile-id=0 \
    --bot-mode=react_bot --bot-llm-name=gpt-4o \
    --api-mode=llm --api-llm-name=gpt-4o \
    --user-template-fn=baselines/user_llm.jinja --bot-template-fn=baselines/flowbench.jinja \
    --conversation-turn-limit=20 --log-utterence-time --log-to-db
```

## Updates

- 241121
    - 完成UI中控制controllers
    - 分离 refresh 逻辑 (workflow, bot, controller, api)
- 241119
    - 更新API定义为OpenAI格式;
    - 实现 RequestAPIHandler
    - 完成 agent-pdl 的UI迁移 (heavy work)
