""" 
TODO:
- [ ] buld typing for workflow
    - [ ] nodes (node data)
    - [ ] input / output (reference)
- [ ] use LLM to generate summary for each node
- [ ] draw node graph (e.g. with graphviz | pyecharts)
- [ ] implement WorkflowPDLConverter
"""

from ..workflow.data_manager import DataManager

data_manager = DataManager()

class WorkflowPDLConverter:
    def __init__(self, data_version: str="huabu_1127", export_version: str="export-1732628942") -> None:
        self.data_version = data_version
        self.export_version = export_version

    def convert(self):
        pass

