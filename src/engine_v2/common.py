import os, datetime
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional
from colorama import init, Fore, Style
init(autoreset=True)        # Reset color to default (autoreset=True handles this automatically)

_file_dir_path = Path(__file__).resolve().parent
DIR_data_base = (_file_dir_path / "../../data/v240628").resolve()
DIR_log = DIR_data_base / "engine_v2_log"
os.makedirs(DIR_log, exist_ok=True)

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
    log_dir: str = DIR_log
    log_fn:str = "tmp.log"
    
    def __init__(self, log_dir:str=DIR_log):
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