import yaml

from common import Config
from data import PDL, DataManager


cfg = Config.from_yaml("default.yaml")
data_manager = DataManager(cfg)

fn = data_manager.DIR_data_workflow / "pdl/000.yaml"
pdl = PDL.load_from_file(fn)


def format_yaml():
    s = pdl.to_str()
    d = yaml.safe_load(s)
    pdl_new = PDL(**d)
    return pdl_new


def format_str():
    s = str(pdl)
    d = yaml.safe_load(s)
    pdl_new = PDL(**d)
    return pdl_new


format_yaml()
format_str()
