import os, datetime, traceback
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional
from colorama import init, Fore, Style
init(autoreset=True)        # Reset color to default (autoreset=True handles this automatically)

from engine_v1.common import (
    init_client, LLM_CFG, DataManager
)


_file_dir_path = Path(__file__).resolve().parent
# model
DIR_templates = (_file_dir_path / "../utils/templates").resolve()
# data
DIR_data_base = (_file_dir_path / "../../data/v240628").resolve()
DIR_huabu_step3 = DIR_data_base / "huabu_step3"
DIR_simulated_base = DIR_data_base / "simulated"
FN_api_infos = DIR_data_base / "apis_v0/apis.json"
DIR_conversation_v1 = DIR_data_base / "conversation_v01"
# log
DIR_engine_v2_log = DIR_data_base / "engine_v2_log"
DIR_simulation_v2_log = DIR_data_base / "simulation_v2_log"
os.makedirs(DIR_engine_v2_log, exist_ok=True)
os.makedirs(DIR_simulation_v2_log, exist_ok=True)

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
    log_dir: str = DIR_engine_v2_log
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
    def __init__(self, log_dir:str=DIR_engine_v2_log):
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

    def log(self, message:str, add_line=True, with_print=False):
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