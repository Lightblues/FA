import os, datetime, traceback, functools, tabulate
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
from colorama import init, Fore, Style
init(autoreset=True)        # Reset color to default (autoreset=True handles this automatically)
import pandas as pd

COLOR_DICT = defaultdict(lambda: Style.RESET_ALL)
COLOR_DICT.update({
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
})

class LogUtils:
    @staticmethod
    def prompt_user_input(prompt_text, prompt_color='blue', input_color='bold_blue'):
        """ styled user input """
        user_input = input(COLOR_DICT[prompt_color] + prompt_text + COLOR_DICT[input_color])
        print(Style.RESET_ALL, end='')
        return user_input
    
    @staticmethod
    def format_infos_with_tabulate(
        infos: Any, 
        tablefmt='psql', maxcolwidths=100,
        color: str = None, auto_transform: bool = True
    ) -> str:
        """ format infos tables with tabulate """
        if isinstance(infos, dict):
            infos = pd.DataFrame([infos]).T
        elif isinstance(infos, pd.DataFrame):
            pass
        elif isinstance(infos, (list, tuple)):
            if isinstance(infos[0], (list, tuple)):
                infos = pd.DataFrame(infos)
            else:
                infos = pd.DataFrame([infos]).T
        elif isinstance(infos, (str, int, float)):
            infos = str(infos)
            infos = pd.DataFrame([infos.split('\n')]).T
        else:
            raise NotImplementedError
        # smartly .T the df?
        if auto_transform:
            if infos.shape[1] > infos.shape[0]:
                infos = infos.T
        
        # 预处理字符串，处理换行符
        def preprocess_string(s):
            return s.split('\n')
        for col in infos.columns:
            infos[col] = infos[col].apply(lambda x: preprocess_string(str(x)) if isinstance(x, str) else x)
        infos_str = tabulate.tabulate(infos, tablefmt=tablefmt, maxcolwidths=maxcolwidths)

        if color is not None:
            infos_str = COLOR_DICT[color] + infos_str + Style.RESET_ALL
        return infos_str

    @staticmethod
    def format_str_with_color(text: str, color: str = 'blue') -> str:
        return COLOR_DICT[color] + text + Style.RESET_ALL


class BaseLogger:
    """ Base logger without dumping to file """
    def __init__(self):
        pass
    def log(self, message:str, with_print=False, *args, **kwargs):
        if with_print:
            print(message)
    def debug(self, message:str, *args, **kwargs):
        print(message)

    def log_to_stdout(self, message:str, color=None):
        colored_message = COLOR_DICT[color] + message + Style.RESET_ALL
        print(colored_message)


class FileLogger(BaseLogger):
    """ Local file logger """
    log_dir: Union[str, Path] = None
    log_fn: Union[str, Path] = None
    log_detail_fn: Union[str, Path] = None
    
    num_logs = 0
    logger_id: str = "tmp"
    def __init__(self, log_dir:str, t:datetime.datetime=None):
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
        _log_subdir = f"{log_dir}/{s_day}"
        os.makedirs(_log_subdir, exist_ok=True)
        self.log_fn = f"{_log_subdir}/{s_millisecond}.log"
        log_detail_fn = f"{_log_subdir}/{s_millisecond}_detail.log"
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


if __name__ == '__main__':
    infos = dict(a=1223, b="ss")
    infos = "This is a string that needs to be highlighted with borders.\nAnother line. "
    print(LogUtils.format_infos_with_tabulate(infos))
    print()

