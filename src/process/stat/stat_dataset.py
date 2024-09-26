""" stat the dataset
updated @240925
"""
from flowagent.data import DataManager, Workflow, WorkflowType, Config
from collections import defaultdict

cfg = Config.from_yaml(DataManager.normalize_config_name('default.yaml'))
# cfg.workflow_dataset = "STAR"
cfg.workflow_dataset = "PDL"
data_manager = DataManager(cfg)

class Stat:
    def stat_types(self):
        cnt = defaultdict(int)
        for i in range(data_manager.num_workflows):
            workflow_id = f"{i:03d}"
            workflow = Workflow.load_by_id(
                data_manager=data_manager,
                id=workflow_id, type=cfg.workflow_type,
                # load_user_profiles=(cfg.exp_mode=="session"), load_reference_conversation=(cfg.exp_mode=="turn")
                load_reference_conversation=True
            )
            reference_conversations = workflow.reference_conversations
            for ref in reference_conversations:
                for msg in ref.conversation.msgs:
                    cnt[(msg.role.rolename, msg.type)] += 1
        print(cnt)
        
if __name__ == '__main__':
    stat = Stat()
    stat.stat_types()