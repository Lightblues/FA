""" updated @240904
- basic implementations
    - [x] BaselineController logic @240905
    - [x] logging and metrics -> append prompts to Message
    - [x] data: Workflow abstraction | align with FlowBench 
    - [x] user: add user profiling? aware of workflow?
    - [x] bot implementation
    - [x] api: mimic by LLM? 
- data
    - [x] convert from v240820
    - [x] dataset orginization (Datamanager)
    - [x] whole generation | simulation
    - [x] store the generated conversation data in a database! (with a session_id)
- evaluation
    - [x] start simulations. 
- robustness & accuracy
    - [x] add retry for API or bot? -> how to evaluate?
    - [x] user simulation: make simulated user to be more realistic (shorter utterance, ...)
    - [ ] API: refine the prompt of API simulator

------------------------------ abstraction ------------------------------
Conversation:
    .add_message(msg)
    .to_str()
    .get_last_message()

BaseRole:
    name; cfg; llm; conv; workflow; 
    .process() -> UserOutput, BotOutput, APIOutput
BotOutput: 
    action_type; action; action_input; thought;
    
Workflow:
    name; 
"""
