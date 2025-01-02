from fa_core.data import FunctionDefinition, ToolDefinition, ExtToolSpec, ToolSpec
import yaml

tool_definition = {
    "type": "function",
    "function": {
        "name": "answer_directly",
        "description": "Answer directly for simple objective, and wait for user's response",
        "parameters": {
            "type": "object",
            "properties": {"answer": {"type": "string", "description": "your complete and detailed and formatted answer to user, not a abstract"}},
            "required": ["answer"],
        },
    },
}

tool_sepc_yaml = """
name: check_hospital_exist
description: 校验挂号医院
parameters:
  type: object
  properties:
    hos_name:
      type: string
      name: 医院名称
      description: 医院名称
      enum: ['北京301医院', '北京安贞医院', '北京朝阳医院', '北京大学第一医院', '北京大学人民医院', '北京儿童医院', '北京积水潭医院', '北京世纪坛医院', '北京天坛医院', '北京协和医学院附属肿瘤医院', '北京协和医院', '北京宣武医院', '北京友谊医院', '北京中日友好医院', '北京中医药大学东方医院', '北京中医药大学东直门医院']
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


def test_tool_definition():
    tool = ToolDefinition(**tool_definition)
    print(tool)
    print(type(tool))


def test_tool_spec():
    tool_spec_dict = yaml.safe_load(tool_sepc_yaml)
    print(tool_spec_dict)
    tool_spec_ext = ExtToolSpec(**tool_spec_dict)
    print(tool_spec_ext)

    # test_ext_tool_spec_to_tool_spec
    tool_spec = tool_spec_ext.to_tool_spec()
    print(tool_spec)

    # test tool_spec_to_tool_definition
    tool_definition = tool_spec.to_tool_definition()
    print(tool_definition)


if __name__ == "__main__":
    # test_tool_definition()
    test_tool_spec()
