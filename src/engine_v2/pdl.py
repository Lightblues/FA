import re

class PDL:
    PDL_str: str = None
    
    taskflow_name: str = ""
    taskflow_desc: str = ""
    apis: list = []
    requests: list = []
    answers: list = []
    workflow_str: str = ""      # the core logic of the taskflow
    
    def __init__(self, PDL_str):
        self.PDL_str = PDL_str

    @classmethod
    def load_from_str(cls, PDL_str):
        instance = cls(PDL_str)
        instance.parse_PDL_str()
        return instance
    @classmethod
    def load_from_file(cls, file_path):
        with open(file_path, 'r') as f:
            PDL_str = f.read().strip()
        return cls.load_from_str(PDL_str)

    def parse_PDL_str(self):
        spliter = "\n\n"
        splited_parts = self.PDL_str.split(spliter, 4)    # NOTE: parse according to the header of each part
        for p in splited_parts:
            if p.startswith("APIs"):
                self.apis = self._parse_apis(p)
            elif p.startswith("REQUESTs"):
                self.requests = self._parse_apis(p)
            elif p.startswith("ANSWERs"):
                self.answers = self._parse_apis(p)
            elif p.startswith("==="):
                self.taskflow_name, self.taskflow_desc = self._parse_meta(p)
            else:
                if self.workflow_str:
                    print(f"[WARNING] {self.workflow_str} v.s. {p}")
                self.workflow_str = p
    def _parse_apis(self, s:str):
        apis = s.split("\n-")[1:]
        res = []
        for s_api in apis:
            api = {}
            for line in s_api.strip().split("\n"):
                k,v = line.strip().split(":", 1)
                api[k.strip()] = v.strip()
            res.append(api)
        return res
    def _parse_meta(self, s:str):
        """ recognize `TaskFlowName: {}` and `TaskFlowDesc: {}` """
        reg_taskflow = re.compile(r"TaskFlowName: (.+)")
        reg_taskflow_desc = re.compile(r"TaskFlowDesc: (.+)")
        taskflow = reg_taskflow.search(s).group(1)
        taskflow_desc = reg_taskflow_desc.search(s).group(1)
        return taskflow, taskflow_desc

    def to_str(self):
        return self.PDL_str
    def __str__(self):
        return self.to_str()
    def __repr__(self):
        return self.to_str()