import re, yaml
from dataclasses import dataclass, asdict, field


class MyDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

    def represent_scalar(self, tag, value, style=None):
        if style is None:
            if '\n' in value:
                style = '|'
        return super(MyDumper, self).represent_scalar(tag, value, style)


@dataclass
class PDL:
    PDL_str: str = None
    
    name: str = ""
    desc: str = ""
    desc_detail: str = ""
    apis: list = field(default_factory=list)
    slots: list = field(default_factory=list)
    answers: list = field(default_factory=list)
    procedure: str = ""      # the core logic of the taskflow
    
    version: str = "v2"
    invalid_apis: dict = field(default_factory=dict)
    current_api_status: list = field(default_factory=list)
    
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
        self.name = ob["Name"]
        self.desc = ob["Desc"]
        self.desc_detail = ob.get("Detailed_desc", "")
        self.apis = ob.get("APIs", [])
        self.slots = ob["SLOTs"]
        self.answers = ob["ANSWERs"]
        self.procedure = ob["PDL"]
        self.invalid_apis = {}
        self.current_api_status = []

    def to_str(self):
        return self.PDL_str
    def to_str_wo_api(self):
        infos = asdict(self)
        selected_keys = ["name", "desc", "desc_detail", "slots", "answers", "procedure"]
        infos_selected = {k: infos[k] for k in selected_keys}
        return yaml.dump(infos_selected, sort_keys=False, Dumper=MyDumper, default_flow_style=False)
    
    def add_invalid_apis(self, api_list):
        for api in api_list:
            if api["api_name"] in self.invalid_apis:
                self.invalid_apis[api["api_name"]]["invalid_reason"].extend(api["invalid_reason"])
            else:
                self.invalid_apis[api["api_name"]] = api
    def reset_invalid_api(self):
        if self.invalid_apis:
            self.invalid_apis.clear()
    def get_valid_apis(self):
        return [api for api in self.apis if api["name"] not in self.invalid_apis]
    def to_str_wo_invalid_api(self):
        infos = asdict(self)
        selected_keys = ["name", "desc", "desc_detail", "slots", "answers", "procedure"]
        infos_selected = {k: infos[k] for k in selected_keys}
        infos_selected["api"] = self.get_valid_apis()
        return yaml.dump(infos_selected, sort_keys=False, Dumper=MyDumper, default_flow_style=False)
    
    def add_current_api_status(self, status):
        self.current_api_status.append(status)
    def reset_api_status(self):
        self.current_api_status.clear()
        
    def __repr__(self):
        return self.PDL_str
