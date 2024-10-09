## TODOs

see detailed in [feishu](https://v0r8x11vrv.feishu.cn/docx/WaMfdTbqaoH1WTx9ZDicVAB7nM9)

data

- [x] LLM auto generate node dependencies #2 @0724
- [x] LLM-based PDL generation @0729
    - [ ] other datasets 

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

paper

- [ ] auto conversation simulation (user agent) #1
- [ ] auto conversation evaluation (based on specific PDL) #1
- [ ] auto PDL generation (with user query) [data source: wikihow] #P0
- [ ] baselines
    - [ ] FlowBench 

bugs

- [ ] fix `Current state` info -- action type and # user query
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

