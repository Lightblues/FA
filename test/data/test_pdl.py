import yaml

from fa_core.common import Config
from fa_core.data import PDL, FADataManager
from fa_core.data.pdl.pdl_nodes import ParameterNode


fn = FADataManager.DIR_data_root / "PDL/pdl/000.yaml"
pdl = PDL.load_from_file(fn)


def to_dict():
    pdl_dict = pdl.model_dump()
    print(pdl_dict)
    return pdl_dict


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


def test_pdl_node():
    node = ParameterNode(name="test", desc="test", type="string")
    print(node)
    node = ParameterNode(name="test")
    print(node)


test_pdl_node()
to_dict()

format_yaml()
format_str()
