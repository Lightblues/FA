
- [doc](https://doc.weixin.qq.com/doc/w3_AcMATAZtAPIHNlsq0hVSqOMrN7MdG?scode=AJEAIQdfAAo0K7FgjoAcMATAZtAPI); [board](https://doc.weixin.qq.com/sheet/e3_AcMATAZtAPIaxl2WshdR0KQkIBZdF?scode=AJEAIQdfAAoVOwbP71AcMATAZtAPI&tab=vr5cxl)

## Roadmap

1. Code structure & Docs
    1. Frontend-Backend separation (v0.1.0) #structure
    2. PDL standard #P0 #doc
        - [ ] Add PDL standard #P0 #doc
2. Data & DB & Log
    1. Data convert: Huabu Json -> PDL #auto #P0
        - [ ] Align existed Huabu nodes
        - [ ] LLM auto generate node dependencies #auto
    2. Data collection (for LLM training)
        - [x] Data storage: with `mongodb` (v0.1.0)
    3. Debug & Checking
        - [x] Debug page: `page_inspect.py` (v0.1.0) #ui
3. Features | Functionality
    1. Evaluation
        - [ ] Evaulation: implement evaluation pipeline #auto
    2. Controllers
        - [x] Dependency: PDL controllable/dependency execuation (v0.1.0)
        - [ ] add dependency for ANSWER nodes
    3. Bots
        - [x] FlowBench #baseline
        - [x] CoRE #baseline
    4. Multi-agent (ref: MetaGPT/Coze)
        - [x] Basic: The "main agent" like @sarm (v0.1.0)
    5. Entity linking (v0.1.0)
    6. memory | summary
4. Evaluation & Optimization
    - [ ] Optimization: find the better PDL format #P0 (link 1.2)
        API_check_hospital_exist -> `API.check_hospital_exist`?
    - [ ] Testing:
        - [ ] Procedure compliance in larger graph?
5. Bugs
    - [ ] 点击 "重置对话", DAG controller 状态没有更新.


## Change log
### v0.1.0
- code structure: frontend-backend separation
