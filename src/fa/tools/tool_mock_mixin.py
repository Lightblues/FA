import jinja2
from loguru import logger
from typing import Dict, Any
from common import init_client, json_line


class ToolMockMixin:
    client = init_client("gpt-4o-mini")

    def mock_llm(self, template: str, slots: Dict = {}):
        template = jinja2.Template(template)
        prompt = template.render(**slots)
        response = self.client.query_one(query=prompt)
        logger.info(f"> Mocked result of {json_line(prompt)}: {json_line(response)}")
        return response

    def mock_code_executor(self, code: str, params: Dict = {}) -> Any:
        """
        Mock the code executor tool

        The description of the code executor node:
            仅支持数据转换或运算等操作, 请勿手动import, 已引入numpy和pandas以及部分内置的运算相关的包；不支持IO操作，如读取文件，网络通信等。
            请保存函数名为main,输入输出均为dict；最终结果会以json字符串方式返回，请勿直接返回不支持json.dumps的对象（numpy和pandas已增加额外处理）

        Sample code::

            def main(params: dict) -> dict:
                data_time = params.get("data", [])
                if len(data_time) == 0:
                    return {"g_time": "", "num_type": ""}
                return {"g_time": data_time[0]["time"], "num_type": data_time[0]["num_type"]}
        """
        # import numpy and pandas & prepare namespace
        import numpy as np
        import pandas as pd

        namespace = {"np": np, "pd": pd}

        try:
            # Try to execute the code with `main` function
            exec(code, namespace)
            result = namespace["main"](params)
            return result

        except Exception as e:
            logger.error(f"Error executing of code {json_line(code)}, Error: {e}")
            return {
                "error": str(e),
                "message": f"Code execution failed! You can try to skip this tool or fix the input!",
                "code": code,
                "params": params,
            }
