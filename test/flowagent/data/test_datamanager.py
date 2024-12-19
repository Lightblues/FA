from common import Config
from flowagent.data import DataManager


cfg = Config.from_yaml("default.yaml")
data_manager = DataManager(cfg)
template_list = data_manager.get_template_name_list()
print(template_list)
print()
