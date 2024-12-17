"""
NOTE: hasn't been used yet!
"""

from typing import *

from pydantic import BaseModel


class _NodeUIDataOutput(BaseModel):
    # [{'id': '42ede01b-9037-4952-5422-5610aebcdff5', 'value': 'Output', 'label': 'Output', 'type': 'OBJECT', 'children': [{'id': '9afe3901-1acc-c2c6-3bbc-364dcddf5c31', 'value': 'invoicing_method', 'label': 'invoicing_method', 'type': 'STRING', 'children': []}]}]
    id: str
    value: str
    label: str
    type: str
    children: List[Any]


class _NodeUIData(BaseModel):
    content: List[Dict[str, Any]]
    isHovering: bool
    isParallel: bool
    source: bool
    target: bool
    debug: Any
    error: bool
    output: List[_NodeUIDataOutput]


class _NodeUI(BaseModel):
    data: _NodeUIData
    position: Dict[str, Any]
    targetPosition: str
    sourcePosition: str
    selected: bool
    measured: Dict[str, Any]
    dragging: bool
