import json
import re
import traceback
from typing import Dict

import yaml


class Formater:
    """用于从字符串中提取信息, 比如规范GPT输出的结果"""

    @staticmethod
    def re_backtick(text):
        """识别反引号 ```xxx``` 包裹的内容"""
        # 设置 ? 非贪婪模式
        # re.DOTALL 使得 . 可以匹配换行符
        pattern = re.compile(r"```(.*?)```", re.DOTALL)
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
        else:
            return None

    @staticmethod
    def re_xml(text):
        """识别 <输入>xxx</输入> 包裹的内容 (query)"""
        # # 1. remove the prefix —— 可以做一些预处理
        # idx = text.find("</参考槽位介绍>")
        # if idx == -1:
        #     print(text)
        #     return None
        # text = text[idx:]
        # 2. extract the query
        pattern = re.compile(r"(?s)<输入>(.*?)</输入>", re.DOTALL)
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
        else:
            return None

    @staticmethod
    def re_xml_all(text):
        pattern = re.compile(r"(?s)<输入>(.*?)</输入>", re.DOTALL)
        matched = pattern.findall(text)
        return matched

    @staticmethod
    def remove_code_prefix(text, type="json"):
        """解析句子中的 代码块 (前后```包裹)，并移除代码前缀"""
        pattern_code = re.compile(r"```(.*?)```", re.DOTALL)
        match = pattern_code.search(text)
        if match:
            text = match.group(0).strip()
        else:
            return text

        pattern = re.compile(f"```{type}\n?", re.IGNORECASE)
        text = pattern.sub("", text)
        pattern = re.compile(f"```", re.DOTALL)
        text = pattern.sub("", text)
        return text.strip()

    @staticmethod
    def parse_codeblock(text: str, type="json") -> str:
        """parse codeblock with specific ```type identifier"""
        pattern = re.compile(f"```{type}\n?(.*?)```", re.DOTALL)
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
        else:
            return text

    @staticmethod
    def parse_json_or_eval(text: str) -> Dict:
        """try eval(x) first, then json.loads(x)"""
        try:
            return eval(text)
        except Exception as e:
            return json.loads(text)

    @staticmethod
    def parse_llm_output_json(text: str) -> Dict:
        """解析 LLM 的输出
        text: 要求json格式的字符串
        """
        try:
            # json_str = re.search(r'\{.*\}', text, flags=re.DOTALL).group()  # 从字符串中提取 JSON 部分
            # json_str = Formater.remove_code_prefix(text, type="json")
            json_str = Formater.parse_codeblock(text, type="json")
            parsed = Formater.parse_json_or_eval(json_str)  # 再进行一次 JSON 解析, 得到结构化的内容
            return parsed
        except Exception as e:
            # print(f"[ERROR] parse_llm_output_json: {e}\n  {text}")
            traceback.print_exc()
            return {"error": str(e), "text": text}

    @staticmethod
    def parse_llm_output_yaml(text: str) -> Dict:
        try:
            yaml_str = Formater.parse_codeblock(text, type="yaml")
            parsed = yaml.safe_load(yaml_str)
            return parsed
        except Exception as e:
            print(f"[ERROR] parse_llm_output_yaml: {e}\n  {text}")
            return {"error": str(e), "text": text}
