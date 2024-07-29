import re, yaml

class PDL_v2:
    """ V2: 直接用yaml格式定义PDL
    不支持PDL内容的修改
    """
    PDL_str: str = None
    
    taskflow_name: str = ""
    taskflow_desc: str = ""
    apis: list = []
    slots: list = []
    answers: list = []
    workflow_str: str = ""      # the core logic of the taskflow
    
    version: str = "v2"
    
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
        ob = yaml.load(self.PDL_str, Loader=yaml.FullLoader)
        self.taskflow_name = ob["Name"]
        self.taskflow_desc = ob["Desc"]
        self.apis = ob.get("APIs", [])
        self.slots = ob["SLOTs"]
        self.answers = ob["ANSWERs"]
        self.workflow_str = ob["PDL"]

    def to_str(self):
        return self.PDL_str
    def __repr__(self):
        return self.PDL_str