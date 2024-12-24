from data.pdl.pdl_nodes import ParameterNode
from .base import TypeEnum
from pydantic import BaseModel
from typing import Any
from fa_core.common import json_line


class Parameter(BaseModel):
    """Parameter
    {'workflow_id': '67a4f791-dd03-44f5-b89d-2992f9fba3d0', 'workflow_node_id': '5d1e2abc-3308-b490-7ff0-591f6ec9f640', 'workflow_node_name': '订单、会员卡id、姓名参数', 'parameter_id': '03882afc-e74b-42a2-b4d7-b28594a0e3b3', 'parameter_name': '会员卡ID', 'parameter_desc': '用户的会员卡ID号码，一般是一串阿拉伯数字', 'parameter_type': 'STRING', 'parameter_correct_example': '[]', 'parameter_wrong_example': '[]'}
    """

    workflow_id: str
    workflow_node_id: str  # the linked API node id
    workflow_node_name: str
    parameter_id: str
    parameter_name: str
    parameter_desc: str
    parameter_type: TypeEnum
    parameter_correct_example: str = None
    parameter_wrong_example: str = None

    def model_post_init(self, __context: Any) -> None:
        self.parameter_desc = json_line(self.parameter_desc)

    def __str__(self):
        return f"Parameter(name={self.parameter_name}, id={self.parameter_id}, desc={self.parameter_desc}, type={self.parameter_type})"

    def to_pdl(self) -> ParameterNode:
        return ParameterNode(name=self.parameter_name, desc=self.parameter_desc, type=self.parameter_type.value.lower())
