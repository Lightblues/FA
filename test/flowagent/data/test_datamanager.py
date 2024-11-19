from flowagent.data import DataManager, Config

cfg = Config.from_yaml(DataManager.normalize_config_name('default.yaml'))
data_manager = DataManager(cfg)
template_list = data_manager.get_template_name_list()
print(template_list)
print()