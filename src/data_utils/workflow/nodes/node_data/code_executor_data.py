from pydantic import BaseModel
from typing import *
from .base import NodeDataBase

class CodeExecutorNodeData(NodeDataBase):
    """ 
        "Code": "\n# 仅支持数据转换或运算等操作, 请勿手动import, 已引入numpy和pandas以及部分内置的运算相关的包；不支持IO操作，如读取文件，网络通信等。\n# 请保存函数名为main,输入输出均为dict；最终结果会以json字符串方式返回，请勿直接返回不支持json.dumps的对象（numpy和pandas已增加额外处理）\ndef main(params: dict) -> dict:\n    data_time = params.get(\"data\", [])\n    if len(data_time) == 0:\n        return {'g_time':'', 'num_type':''}\n    return {\n        'g_time': data_time[0][\"time\"],\n        \"num_type\": data_time[0][\"num_type\"]\n    }\n",
        "Language": "PYTHON3"
    """
    Code: str
    Language: str
