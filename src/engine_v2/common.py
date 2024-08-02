import os, datetime, traceback, functools
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional, Union
from colorama import init, Fore, Style
init(autoreset=True)        # Reset color to default (autoreset=True handles this automatically)

from engine_v1.common import (
    init_client, LLM_CFG
)

DEBUG = False
# DEBUG = True      # NOTE: switch it on for debug

class DirectoryManager:
    def __init__(self):
        _file_dir_path = Path(__file__).resolve().parent
        _dir_data_base = (_file_dir_path / "../../data/v240628").resolve()
        _dir_src_base = (_file_dir_path / "../../src").resolve()
        self.DIR_data_base = _dir_data_base
        self.DIR_src_base = _dir_src_base
        
        self.DIR_templates = _dir_src_base / "utils/templates"
        self.DIR_engine_v2_config = _dir_src_base / "engine_v2/configs"
        
        self.DIR_huabu_step3 = _dir_data_base / "huabu_step3"
        self.DIR_huabu_meta = _dir_data_base / "huabu_meta"
        self.DIR_simulated_base = _dir_data_base / "simulated"
        self.DIR_conversation_v1 = _dir_data_base / "conversation_v01"
        self.FN_api_infos = _dir_data_base / "apis_v0/apis.json"

        self.DIR_engine_v2_log = _dir_data_base / "engine_v2_log"
        self.DIR_simulation_v2_log = _dir_data_base / "simulation_v2_log"
        self.DIR_ui_v2_log = _dir_data_base / "ui_v2_log"
        os.makedirs(self.DIR_engine_v2_log, exist_ok=True)
        os.makedirs(self.DIR_simulation_v2_log, exist_ok=True)
        os.makedirs(self.DIR_ui_v2_log, exist_ok=True)
        
        self.HUABU_versions = ["huabu_step3_v01", "huabu_step3", "huabu_manual", "huabu_refine01"]
        self.HUABU_versions_pdl2 = ["huabu_step3", "huabu_manual", "huabu_refine01"]

_DIRECTORY_MANAGER = DirectoryManager()

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
    def __init__(self, log_dir:str=_DIRECTORY_MANAGER.DIR_engine_v2_log):
        """ 
        args:
            log_dir: str, the directory to save the log files
        """
        super().__init__()
        now = datetime.datetime.now()
        s_day = now.strftime("%Y-%m-%d")
        s_second = now.strftime("%Y-%m-%d_%H-%M-%S")
        s_millisecond = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        
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
    def build_workflow_id_map(workflow_dir:str, extension:str=".txt"):
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
    def get_workflow_name_list(workflow_dir:str, extension:str=".txt"):
        fns = [fn.rstrip(extension) for fn in os.listdir(workflow_dir) if fn.endswith(extension)]
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
    def normalize_workflow_name(workflow_name:str, workflow_dir:str, extension:str=".txt"):
        workflow_dir = DataManager.normalize_workflow_dir(workflow_dir)
        workflow_name_map = DataManager.build_workflow_id_map(workflow_dir, extension=extension)
        assert workflow_name in workflow_name_map, f"Unknown workflow_name: {workflow_name}! Please choose from {workflow_name_map.keys()}"
        return workflow_name_map[workflow_name]

    @staticmethod
    def normalize_config_name(config_name:str):
        config_fn = f"{_DIRECTORY_MANAGER.DIR_engine_v2_config}/{config_name}"
        return config_fn
    
    @staticmethod
    def normalize_pdl_version(pdl_version:str="", workflow_dir:str=""):
        if pdl_version: return pdl_version
        if not workflow_dir: raise ValueError("workflow_dir is required!")
        subfolder_name = workflow_dir.split("/")[-1]
        if subfolder_name in _DIRECTORY_MANAGER.HUABU_versions:
            return "v1"
        elif subfolder_name in _DIRECTORY_MANAGER.HUABU_versions_pdl2:
            return "v2"
        else:
            raise ValueError(f"Unknown workflow_dir: {workflow_dir}! Please choose from {_DIRECTORY_MANAGER.HUABU_versions} or {_DIRECTORY_MANAGER.HUABU_versions_pdl2}")