## TODOs

data

- [x] LLM auto generate node dependencies #2 @0724
- [x] LLM-based PDL generation @0729

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

bugs

- [ ] fix `Current state` info -- action type and # user query
- [x] fix: entity linking result write back to Message  #1 @240821
- [x] V2: remove `REQUEST` type @240821

## run

```sh
PROJECT_PATH=/apdcephfs_cq8/share_2992827/shennong_5/easonsshi/huabu
cd ${PROJECT_PATH}/src

# 运行交互, 在交互的时候参见 huabu PDL 数据
python main.py --model_name qwen2_72B --api_mode manual --template_fn query_PDL_v01.jinja --workflow_name 005  # workflow_name 即画布名称/ID, 见 huabu PDL 路径
```

