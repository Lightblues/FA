from dataclasses import asdict, dataclass, field
from typing import Dict, List

import yaml


class MyDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

    def represent_scalar(self, tag, value, style=None):
        if style is None:
            if "\n" in value:
                style = "|"
        return super(MyDumper, self).represent_scalar(tag, value, style)


@dataclass
class PDL:
    PDL_str: str = None

    Name: str = ""
    Desc: str = ""
    Desc_detail: str = ""
    APIs: list = field(default_factory=list)
    SLOTs: list = field(default_factory=list)
    ANSWERs: list = field(default_factory=list)
    Procedure: str = ""  # the core logic of the taskflow

    invalid_apis: Dict[str, Dict] = field(default_factory=dict)  # {name: {api_name, [invalid_reason]}}
    current_api_status: List[str] = field(default_factory=list)  # strings that descripts api status

    status_for_prompt: Dict[str, str] = field(default_factory=dict)

    def __init__(self, PDL_str):
        self.PDL_str = PDL_str

    @classmethod
    def load_from_str(cls, PDL_str):
        instance = cls(PDL_str)
        instance.parse_PDL_str()
        return instance

    @classmethod
    def load_from_file(cls, file_path):
        with open(file_path, "r") as f:
            PDL_str = f.read().strip()
        return cls.load_from_str(PDL_str)

    def parse_PDL_str(self):
        ob = yaml.load(self.PDL_str, Loader=yaml.FullLoader)
        self.Name = ob["Name"]
        self.Desc = ob["Desc"]
        self.Desc_detail = ob.get("Detailed_desc", "")
        self.APIs = ob.get("APIs", [])
        self.SLOTs = ob["SLOTs"]
        self.ANSWERs = ob["ANSWERs"]
        self.Procedure = ob["PDL"]

        self.invalid_apis = {}
        self.current_api_status = []
        self.status_for_prompt = {}

    def to_str(self):
        return self.PDL_str.strip()

    def to_str_wo_api(self):
        infos = asdict(self)
        selected_keys = ["Name", "Desc", "Desc_detail", "SLOTs", "ANSWERs", "Procedure"]
        infos_selected = {k: infos[k] for k in selected_keys}
        return yaml.dump(
            infos_selected,
            sort_keys=False,
            Dumper=MyDumper,
            default_flow_style=False,
            allow_unicode=True,
        ).strip()

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
        return [api for api in self.APIs if api["name"] not in self.invalid_apis]

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
