from flowagent.roles.tools.entity_linker import EntityLinker
from flowagent.data import Config, DataManager

cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))

entity_linker = EntityLinker(cfg=cfg)

res = entity_linker.entity_linking("朝阳医院", ['北京301医院', '北京安贞医院', '北京朝阳医院', '北京大学第一医院', '北京大学人民医院', '北京儿童医院', '北京积水潭医院', '北京世纪坛医院', '北京天坛医院', '北京协和医学院附属肿瘤医院', '北京协和医院', '北京宣武医院', '北京友谊医院', '北京中日友好医院', '北京中医药大学东方医院', '北京中医药大学东直门医院'])
print(res)
print()
