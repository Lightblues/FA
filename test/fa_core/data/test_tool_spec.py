import pytest
import yaml
from fa_core.data import FunctionDefinition, ToolDefinition, ExtToolSpec, ToolSpec


@pytest.fixture
def tool_spec_yaml():
    return """
name: check_hospital_exist
description: 校验挂号医院
parameters:
    type: object
    properties:
        hos_name:
            type: string
            name: 医院名称
            description: 医院名称
    required:
    - hos_name
response:
    type: object
    properties:
    type:
        type: string
        name: 医院存在类型
        description: 输出内容
url: http://8.134.222.238:8091/check-hospital-exist
method: GET
""".strip()


@pytest.fixture
def tool_definition():
    return {
        "type": "function",
        "function": {
            "name": "answer_directly",
            "description": "Answer directly for simple objective, and wait for user's response",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "your complete and detailed and formatted answer to user, not a abstract"}
                },
                "required": ["answer"],
            },
        },
    }


@pytest.mark.unit
class TestToolDefinition:
    def test_tool_definition_creation(self, tool_definition):
        """测试工具定义的创建"""
        tool = ToolDefinition(**tool_definition)
        assert isinstance(tool, ToolDefinition)
        assert tool.type == "function"
        assert tool.function.name == "answer_directly"
        assert "answer" in tool.function.parameters.properties


@pytest.mark.unit
class TestToolSpec:
    def test_tool_spec_creation(self, tool_spec_yaml):
        """test tool spec creation and conversion"""
        tool_spec_dict = yaml.safe_load(tool_spec_yaml)
        tool_spec_ext = ExtToolSpec(**tool_spec_dict)
        assert isinstance(tool_spec_ext, ExtToolSpec)
        assert tool_spec_ext.name == "check_hospital_exist"

        # test conversion to ToolSpec
        tool_spec = tool_spec_ext.to_tool_spec()
        assert isinstance(tool_spec, ToolSpec)
        assert tool_spec.name == "check_hospital_exist"

        # test conversion to ToolDefinition
        tool_definition = tool_spec.to_tool_definition()
        assert isinstance(tool_definition, ToolDefinition)
        assert tool_definition.type == "function"

    def test_tool_spec_parameters(self, tool_spec_yaml):
        """test tool spec parameters validation"""
        tool_spec_dict = yaml.safe_load(tool_spec_yaml)
        tool_spec_ext = ExtToolSpec(**tool_spec_dict)

        # validate parameters definition
        assert "hos_name" in tool_spec_ext.parameters.properties
        assert tool_spec_ext.parameters.properties["hos_name"].type == "string"
