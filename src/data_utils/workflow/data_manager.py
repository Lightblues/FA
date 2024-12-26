"""

## 节点类型
> 共享属性: ['NodeID', 'NodeName', 'NodeDesc', 'NodeType', 'Inputs', 'Outputs', 'NextNodeIDs', 'NodeUI']
- CODE_EXECUTOR: 代码执行节点, 主要用于参数处理
    NOTE: 暂不考虑
- PARAMETER_EXTRACTOR: 参数提取节点, #LLM 生成问题
    Parameters 定义了所引用的参数 (参数.xlsx);
    UserConstraint: '当需要对“包裹内容”参数进行追问时，请严格按照以下内容进行追问：“请问您需要寄送什么物品？”'
    NOTE: 可以提取出其中的 `UserConstraint`
- LLM: 大模型节点, 使用大模型进行结果转换
    Prompt: '请将国家名称{{countryName}} 转换为对应的ISO 3166-1二位字母代码；如将"中国"转换为"CN"; "美国"转换为"US"; "德国"转换为"DE"。请直接返回结果'}
    NOTE: 封装为 #tool
- LLM_KNOWLEDGE_QA: 大模型知识问答节点, 使用大模型进行知识问答
    NOTE: 封装为 #tool
- LOGIC_EVALUATOR: 逻辑评估节点, 评估逻辑
    NOTE: 存在复杂的结构 (条件判断1 in "这个物品可以寄送吗"), 需要验证转换成功率
- ANSWER: 答案节点, 定义固定回复
- KNOWLEDGE_RETRIEVER: 知识检索节点, 纯 retrieval
    NOTE: 封装为 #tool
- START: 开始节点, 开始工作流
- TOOL: 工具节点, 使用工具
    NOTE: 简单转换以支持

--- v241127 export-1732628942 ---
000: 快递费用和到达时间是多少
001: 同程开发票
002: 订餐流程
003: 礼金礼卡案件办理
004: 酒店取消订单
005: 比较两个文档的核心差异
006: 挂号
007: 这个物品可以寄送吗

--- workflow node type stat ---
000 [快递费用和到达时间是多少]: Counter({'LOGIC_EVALUATOR': 25, 'PARAMETER_EXTRACTOR': 23, 'ANSWER': 16, 'TOOL': 8, 'START': 1, 'LLM': 1})
001 [同程开发票]: Counter({'ANSWER': 13, 'LOGIC_EVALUATOR': 5, 'TOOL': 3, 'PARAMETER_EXTRACTOR': 3, 'START': 1})
002 [订餐流程]: Counter({'ANSWER': 11, 'PARAMETER_EXTRACTOR': 5, 'LOGIC_EVALUATOR': 5, 'TOOL': 2, 'START': 1})
004 [酒店取消订单]: Counter({'ANSWER': 13, 'LOGIC_EVALUATOR': 5, 'TOOL': 4, 'CODE_EXECUTOR': 4, 'PARAMETER_EXTRACTOR': 2, 'START': 1})
006 [挂号]: Counter({'ANSWER': 16, 'LOGIC_EVALUATOR': 10, 'TOOL': 7, 'PARAMETER_EXTRACTOR': 6, 'LLM': 2, 'START': 1, 'CODE_EXECUTOR': 1})
007 [这个物品可以寄送吗]: Counter({'LOGIC_EVALUATOR': 17, 'PARAMETER_EXTRACTOR': 15, 'ANSWER': 13, 'TOOL': 2, 'LLM': 2, 'START': 1})

003 [礼金礼卡案件办理]: Counter({'PARAMETER_EXTRACTOR': 5, 'ANSWER': 5, 'LOGIC_EVALUATOR': 4, 'START': 1, 'LLM_KNOWLEDGE_QA': 1, 'CODE_EXECUTOR': 1})
005 [比较两个文档的核心差异]: Counter({'PARAMETER_EXTRACTOR': 2, 'ANSWER': 2, 'KNOWLEDGE_RETRIEVER': 2, 'LLM': 2, 'START': 1, 'LOGIC_EVALUATOR': 1})
"""

import collections
import json
import pathlib
from typing import *
from pydantic import BaseModel
import pandas as pd

from .parameter import Parameter
from .workflow import Workflow


class WorkflowDataManager(BaseModel):
    DIR_root: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent.parent.parent
    DIR_data: pathlib.Path = DIR_root / "data"
    DIR_dataset: pathlib.Path = DIR_root / "dataset"

    data_version: str = "v241127"
    export_version: str = "export-1732628942"
    workflow_infos: Dict[str, Dict[str, str]] = {}
    parameter_infos: Dict[str, Parameter] = {}

    def model_post_init(self, __context: Any) -> None:
        self.workflow_infos = self._load_workflow_infos()
        self.parameter_infos = self._load_parameter_infos()

    def get_task_infos(self) -> Dict[str, Dict[str, str]]:
        """Get the standard task infos
        Format: { "000": { "name": "114挂号", "task_description": "提供挂号服务, 为用户查询和推荐北京相关医院和科室" }, ... }
        """
        task_infos = {}
        for workflow_id, workflow_info in self.workflow_infos.items():
            task_infos[workflow_id] = {
                "name": workflow_info["workflow_name"],
                "task_description": workflow_info["workflow_desc"],
            }
        return task_infos

    def _load_workflow_infos(self, verbose: bool = False):
        """Load the workflow infos from the excel file.
        1. rename the columns to ['workflow_id', 'workflow_name', 'workflow_desc', 'workflow_fn']
        2. output: { "000": { key: value } }
        """
        fn = self.DIR_data / self.data_version / self.export_version / "工作流程.xlsx"
        df = pd.read_excel(fn)
        columns_old = ["工作流ID", "工作流名称", "工作流描述", "画布结构"]
        columns_new = ["workflow_id", "workflow_name", "workflow_desc", "workflow_fn"]
        df.rename(columns=dict(zip(columns_old, columns_new)), inplace=True)
        res = {}
        for idx, row in df.iterrows():
            res[f"{idx:03d}"] = {
                "workflow_id": row["workflow_id"],
                "workflow_name": row["workflow_name"],
                "workflow_desc": row["workflow_desc"],
                "workflow_fn": row["workflow_fn"],
            }
        # print the id to name mapping
        if verbose:
            print(f"--- {self.data_version} {self.export_version} ---")
            for id, info in res.items():
                print(f"  {id}: {info['workflow_name']}")
        return res

    def _load_parameter_infos(self, verbose: bool = False) -> Dict[str, Parameter]:
        """Load parameter infos
        Output: { id: {infos} }
        """
        fn = self.DIR_data / self.data_version / self.export_version / "参数.xlsx"
        df = pd.read_excel(fn)
        columns_old = [
            "工作流ID",
            "工作流节点ID",
            "工作流节点名称",
            "参数ID",
            "参数名称",
            "参数描述",
            "参数类型",
            "参数正确示例",
            "参数错误示例",
        ]
        columns_new = [
            "workflow_id",
            "workflow_node_id",
            "workflow_node_name",
            "parameter_id",
            "parameter_name",
            "parameter_desc",
            "parameter_type",
            "parameter_correct_example",
            "parameter_wrong_example",
        ]
        df.rename(columns=dict(zip(columns_old, columns_new)), inplace=True)
        res = {}
        for idx, row in df.iterrows():
            data = row.to_dict()
            # NOTE: remove values with NaN
            data = {k: v for k, v in data.items() if not pd.isna(v)}
            res[row["parameter_id"]] = Parameter(**data)
        return res

    def get_standard_workflow_id(self, workflow_id: Union[str, int]):
        """Convert the workflow id to the standard format"""
        if isinstance(workflow_id, int):
            workflow_id = f"{workflow_id:03d}"
        assert workflow_id in self.workflow_infos, f"workflow_id {workflow_id} not found"
        return workflow_id

    def get_workflow_by_id(
        self,
        workflow_id: Union[str, int],
        verbose: bool = False,
    ) -> Workflow:
        """Get the workflow by id"""
        workflow_id = self.get_standard_workflow_id(workflow_id)
        fn = self.DIR_data / self.data_version / self.export_version / self.workflow_infos[workflow_id]["workflow_fn"]
        workflow = json.load(open(fn, "r", encoding="utf-8"))
        workflow["Edges"] = json.loads(workflow.pop("Edge"))
        if verbose:
            print(f"--- Loaded [{workflow_id}] {workflow['WorkflowName']} {workflow['WorkflowID']} ---")
        return Workflow(**workflow)

    def stat_node_type(self):
        """Stat the node type distribution of the dataset"""
        print(f"--- workflow node type stat ---")
        for workflow_id, workflow_info in self.workflow_infos.items():
            workflow = self.get_workflow_by_id(workflow_id)
            cnt = collections.Counter([node.NodeType for node in workflow.Nodes])
            print(f"{workflow_id} [{workflow_info['workflow_name']}]: {cnt}")
