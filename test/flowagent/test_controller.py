from flowagent.pdl_controllers import NodeDependencyController
from flowagent.data import Config, Workflow, DataManager, Conversation, BotOutput


def test_dep_controller():
    # {name: "api_duplication", config: {if_pre: true, if_post: true, threshold: 2}}
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    workflow = Workflow(cfg)
    conv = Conversation()
    
    controller = NodeDependencyController(conv=conv, pdl=workflow.pdl, 
        config={"if_pre": True, "if_post": True, "threshold": 2})

    bot_output: BotOutput = BotOutput(action="check_hospital", action_input={"hospital_name": "test"}, response=None)
    res = controller.post_control(bot_output)
    print(f">>> post_control: {res}")

    controller.pre_control(bot_output)
    print(f">>> pre_control: {controller.pdl.status_for_prompt}")
    print()
    
test_dep_controller()