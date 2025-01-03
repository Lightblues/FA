import pytest
import yaml

from fa_core.data import PDL, FADataManager
from fa_core.data.pdl.pdl_nodes import ParameterNode


@pytest.fixture
def sample_pdl():
    fn = FADataManager.DIR_data_root / "v241127/pdl/000.yaml"
    return PDL.load_from_file(fn)


@pytest.mark.unit
class TestPDL:
    def test_format_str(self, sample_pdl: PDL):
        """test PDL format str"""
        str_repr = str(sample_pdl)
        data = yaml.safe_load(str_repr)
        pdl_new = PDL(**data)
        assert pdl_new.model_dump() == sample_pdl.model_dump()


@pytest.mark.unit
class TestPDLNode:
    @pytest.mark.parametrize(
        "node_data",
        [
            {"name": "test", "desc": "test", "type": "string"},
            {"name": "test"},
        ],
    )
    def test_parameter_node_creation(self, node_data):
        """测试参数节点创建"""
        node = ParameterNode(**node_data)
        assert node.name == "test"
        if "desc" in node_data:
            assert node.desc == "test"
        if "type" in node_data:
            assert node.type == "string"
