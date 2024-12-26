from fa_core.common import Config
from fa_core.data import FADataManager


cfg = Config.from_yaml("default.yaml")
data_manager = FADataManager(workflow_dataset=cfg.workflow_dataset)
template_list = data_manager.get_template_name_list()
print(template_list)
print()
