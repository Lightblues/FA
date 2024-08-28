import os, datetime, traceback, functools
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional, Union
from colorama import init, Fore, Style
init(autoreset=True)        # Reset color to default (autoreset=True handles this automatically)
from easonsi.llm.openai_client import OpenAIClient, Formater


DEBUG = False
DEBUG = True      # NOTE: switch it on for debug

# ===================================== dir manager ==================================================
class DirectoryManager:
    def __init__(self):
        _file_dir_path = Path(__file__).resolve().parent
        _dir_data_base = (_file_dir_path / "../../data/v240820").resolve()
        _dir_src_base = (_file_dir_path / "../../src").resolve()
        self.DIR_data_base = _dir_data_base
        self.DIR_src_base = _dir_src_base
        
        self.DIR_templates = _dir_src_base / "utils/templates"
        self.DIR_engine_v2_config = _dir_src_base / "configs"
        
        self.DIR_huabu_step3 = _dir_data_base / "pdl2_step3"
        self.DIR_huabu_meta = _dir_data_base / "huabu_meta"
        self.DIR_simulated_base = _dir_data_base / "simulated"
        self.DIR_conversation_v1 = _dir_data_base / "conversation_v01"
        self.DIR_user_profile = _dir_data_base / "../gen/user_profile"
        self.FN_api_infos = _dir_data_base / "apis/apis.json"

        self.DIR_engine_v2_log = _dir_data_base / "engine_v2_log"
        self.DIR_simulation_v2_log = _dir_data_base / "simulation_v2_log"
        self.DIR_ui_v2_log = _dir_data_base / "ui_v2_log"
        os.makedirs(self.DIR_engine_v2_log, exist_ok=True)
        os.makedirs(self.DIR_simulation_v2_log, exist_ok=True)
        os.makedirs(self.DIR_ui_v2_log, exist_ok=True)
        
        # self.HUABU_versions = ["huabu_step3_v01", "huabu_step3", "huabu_manual", "huabu_refine01"]
        self.HUABU_versions_pdl2 = ["pdl2_step3"]

_DIRECTORY_MANAGER = DirectoryManager()


# ===================================== log ==================================================
color_dict = defaultdict(lambda: Style.RESET_ALL)
defined_color_dict = {
    'gray': Fore.LIGHTBLACK_EX,
    'orange': Fore.LIGHTYELLOW_EX,
    'red': Fore.RED,
    'green': Fore.GREEN,
    'blue': Fore.BLUE,
    'yellow': Fore.YELLOW,
    'magenta': Fore.MAGENTA,
    'cyan': Fore.CYAN,
    'white': Fore.WHITE, 
    'bold_blue': Style.BRIGHT + Fore.BLUE
}
color_dict.update(defined_color_dict)

def prompt_user_input(prompt_text, prompt_color='blue', input_color='bold_blue'):
    user_input = input(color_dict[prompt_color] + prompt_text + color_dict[input_color])
    print(Style.RESET_ALL, end='')
    return user_input


class BaseLogger:
    log_dir: str = _DIRECTORY_MANAGER.DIR_engine_v2_log
    log_fn:str = "tmp.log"
    def __init__(self):
        pass
    def log(self, *args, **kwargs):
        pass
    def debug(self, *args, **kwargs):
        pass

    def log_to_stdout(self, message:str, color=None):
        colored_message = color_dict[color] + message + Style.RESET_ALL
        print(colored_message)

class Logger(BaseLogger):
    num_logs = 0
    logger_id: str = "tmp"
    def __init__(self, log_dir:str=_DIRECTORY_MANAGER.DIR_engine_v2_log, t:datetime.datetime=None):
        """ 
        args:
            log_dir: str, the directory to save the log files
        """
        super().__init__()
        if not t:
            t = datetime.datetime.now()
        s_day = t.strftime("%Y-%m-%d")
        s_second = t.strftime("%Y-%m-%d_%H-%M-%S")
        s_millisecond = t.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        self.logger_id = s_millisecond
        
        self.log_dir = log_dir
        log_subdir = f"{log_dir}/{s_day}"
        os.makedirs(log_subdir, exist_ok=True)
        self.log_fn = f"{log_subdir}/{s_millisecond}.log"
        log_detail_fn = f"{log_subdir}/{s_millisecond}_detail.log"
        self.log_detail_fn = log_detail_fn
        
        self.num_logs = 0

    def log(self, message:str, add_line=True, with_print=False):
        self.num_logs += 1
        with open(self.log_fn, 'a') as f:
            f.write(message + "\n" if add_line else "")
            f.flush()
        if with_print:
            print(message)
    
    def debug(self, message:str):
        with open(self.log_detail_fn, 'a') as f:
            f.write(f"{message}\n\n")
            f.flush()

# def handle_exceptions(func):
#     """异常捕获, 返回错误信息"""
#     def wrapper(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except Exception as e:
#             # print(e)
#             print(traceback.format_exc())
#             return {'status': 'error', 'message': str(e)}
#     return wrapper

class DataManager:
    @staticmethod
    @functools.lru_cache(maxsize=None)
    def build_workflow_id_map(workflow_dir:str, extension:str=".yaml"):
        workflow_id_map = {}
        for file in os.listdir(workflow_dir):
            if file.endswith(extension):
                # workflow_name = file.rstrip(extension)    # NOTE: error for __x.txt
                workflow_name = file[:-len(extension)]
                id, name = workflow_name.split("-", 1)
                workflow_id_map[id] = workflow_name
                workflow_id_map[name] = workflow_name
                workflow_id_map[workflow_name] = workflow_name
        return workflow_id_map
    @staticmethod
    @functools.lru_cache(maxsize=None)
    def get_workflow_name_list(workflow_dir:str, extension:str=".yaml"):
        fns = [fn[:-len(extension)] for fn in os.listdir(workflow_dir) if fn.endswith(extension)]
        return list(sorted(fns))

    @staticmethod
    def get_template_name_list(template_dir:str, prefix:str="query_"):
        fns = [fn for fn in os.listdir(template_dir) if fn.startswith(prefix)]
        return list(sorted(fns))

    @staticmethod
    def normalize_workflow_dir(workflow_dir:Union[str, Path]):
        # Convert Path to string if necessary
        if isinstance(workflow_dir, Path):
            workflow_dir = str(workflow_dir)
        if not workflow_dir.startswith("/apdcephfs"):
            subfolder_name = workflow_dir.split("/")[-1]
            workflow_dir = _DIRECTORY_MANAGER.DIR_data_base / subfolder_name
        return workflow_dir
    
    @staticmethod
    def normalize_workflow_name(workflow_name:str, workflow_dir:str, extension:str=".yaml"):
        workflow_dir = DataManager.normalize_workflow_dir(workflow_dir)
        workflow_name_map = DataManager.build_workflow_id_map(workflow_dir, extension=extension)
        assert workflow_name in workflow_name_map, f"Unknown workflow_name: {workflow_name}! Please choose from {workflow_name_map.keys()}"
        return workflow_name_map[workflow_name]

    @staticmethod
    def normalize_config_name(config_name:str):
        config_fn = f"{_DIRECTORY_MANAGER.DIR_engine_v2_config}/{config_name}"
        return config_fn


# ===================================== llm ==================================================

LLM_CFG = {
    "custom": {
        "model_name": "Qwen2-72B-Instruct",
        "base_url": "http://9.91.12.44:8000/v1/",
        "api_key": "xxx",
    },
    "v0729-Llama3_1-70B": {
        "model_name": "Infinity-Instruct-7M-0729-Llama3_1-70B",
        "base_url": "http://9.91.12.44:8000/v1/",
        "api_key": "xxx",
    },
    # "gpt-4o": {
    #     "model_name": "gpt-4o",
    #     "base_url": os.getenv("OPENAI_PROXY_BASE_URL"),
    #     "api_key": os.getenv("OPENAI_PROXY_API_KEY"),
    # }
}
def add_openai_models():
    global LLM_CFG
    model_list = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
    for model in model_list:
        LLM_CFG[model] = {
            "model_name": model,
            "base_url": os.getenv("OPENAI_PROXY_BASE_URL"),
            "api_key": os.getenv("OPENAI_PROXY_API_KEY"),
        }
# add models registered in `/apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/model_server/_run_multi_urls.py`
# e.g. WizardLM2-8x22b, qwen2_72B
def add_local_models():
    global LLM_CFG
    import importlib.util
    from urllib.parse import urlparse
    _fn = "/apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/model_server/_run_multi_urls.py"
    spec = importlib.util.spec_from_file_location("model_urls", _fn)
    model_urls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model_urls)
    model_info = {}
    for name, url in model_urls.local_urls.items():     # process the `local_urls` object
        if 'http' not in url: continue
        parsed_url = urlparse(url)
        model_info[name] = f"{parsed_url.scheme}://{parsed_url.netloc}"

    for model, url in model_info.items():
        LLM_CFG[model] = {
            "model_name": model, "base_url": url, 
            "api_key": "xxx",   # NOTE: api_key 不能为 "" 不然也会报错
            "is_sn": True
        }
# set model alias!!
add_openai_models()
add_local_models()
_name_map = {
    "default": "qwen2_72B",
    "0.9.1": "Qwen1.5-72B-4M-1_0_3-Agent-1_2_KU_woClarify_AllRandom",
}
for k,v in _name_map.items():
    LLM_CFG[k] = LLM_CFG[v]
# print(f"[INFO] LLM models: {LLM_CFG.keys()}")

def init_client(llm_cfg:Dict):
    # global client
    base_url = os.getenv("OPENAI_PROXY_BASE_URL") if llm_cfg.get("base_url") is None else llm_cfg["base_url"]
    api_key = os.getenv("OPENAI_PROXY_API_KEY") if llm_cfg.get("api_key") is None else llm_cfg["api_key"]
    model_name = llm_cfg.get("model_name", "gpt-4o")
    client = OpenAIClient(
        model_name=model_name, base_url=base_url, api_key=api_key, is_sn=llm_cfg.get("is_sn", False)
    )
    return client

