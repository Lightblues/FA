
- [doc](https://doc.weixin.qq.com/doc/w3_AcMATAZtAPIHNlsq0hVSqOMrN7MdG?scode=AJEAIQdfAAo0K7FgjoAcMATAZtAPI); [board](https://doc.weixin.qq.com/sheet/e3_AcMATAZtAPIaxl2WshdR0KQkIBZdF?scode=AJEAIQdfAAoVOwbP71AcMATAZtAPI&tab=vr5cxl)

## Roadmap

1. Code structure & Docs
    1. Frontend-Backend separation #structure (v0.1.0)
    2. PDL standard #P0 #doc
        - [ ] Add PDL standard #P0 #doc
2. Data & DB & Log
    1. Data convert: Huabu Json -> PDL #auto #P0
        - [x] Align existed Huabu nodes
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
        - [x] Basic: The "main agent" like @swarm (v0.1.0)
    5. Entity linking (v0.1.0)
    6. FC: try the difference of ReAct & Function calling
        - [x] implement for single-agent. [Observation: FC capability of open-source LLM is pretty bad! (maybe need deep prompt engineering?)]
        - [x] seperate `UISingleBot` & `UISingleFCBot`
    7. memory | summary
4. Evaluation & Optimization
    1. Optimization: find the better PDL format #P0 (link 1.2)
        - [ ] API_check_hospital_exist -> `API.check_hospital_exist`?
    2. Testing:
        - [ ] Procedure compliance in larger graph?
5. Bugs
    - [ ] For "重置对话", the DAG controller state is not reset after clicked.
    - [ ] API dependency is missed in prompt. #P0


## Change log
### v0.1.0
- code structure: frontend-backend separation
