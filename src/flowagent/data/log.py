import os, sys, datetime, traceback, functools, tabulate, pprint, textwrap
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
from colorama import init, Fore, Style
init(autoreset=True)        # Reset color to default (autoreset=True handles this automatically)
import pandas as pd
from loguru import logger
from loguru._logger import Logger

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
    def format_user_input(prompt_text, prompt_color='blue', input_color='bold_blue'):
        """ styled user input """
        user_input = input(COLOR_DICT[prompt_color] + prompt_text + COLOR_DICT[input_color])
        print(Style.RESET_ALL, end='')
        return user_input
    
    @staticmethod
    def format_infos_with_pprint(infos:Any) -> str:
        return pprint.pformat(infos)
    
    @staticmethod
    def format_infos_basic(infos: Any, width: int=100, replace_whitespace: bool=False) -> str:
        """ prefer to format long string """
        if not isinstance(infos, str):
            infos = str(infos)
        
        # Wrap the text to the specified width
        wrapped_text = textwrap.fill(infos, width=width, replace_whitespace=replace_whitespace)
        
        # surround the text with a box
        lines = wrapped_text.split('\n')
        box_width = max(len(line) for line in lines) + 2
        top_border = '+' + '-' * (box_width+2) + '+'
        bottom_border = '+' + '-' * (box_width+2) + '+'
        boxed_text = top_border + '\n'
        for line in lines:
            boxed_text += '| ' + line.ljust(box_width) + ' |\n'
        boxed_text += bottom_border
        
        return boxed_text
    
    @staticmethod
    def format_infos_with_tabulate(
        infos: Any, 
        tablefmt='psql', maxcolwidths=100, headers='keys',
        color: str = None, auto_transform: bool = False
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
        # def preprocess_string(s):
        #     if '\n' in s: s = s.split('\n')
        #     return s
        # for col in infos.columns:
        #     infos[col] = infos[col].apply(lambda x: preprocess_string(str(x)) if isinstance(x, str) else x)
        infos_str = tabulate.tabulate(infos, tablefmt=tablefmt, maxcolwidths=maxcolwidths, headers=headers)

        if color is not None:
            infos_str = COLOR_DICT[color] + infos_str + Style.RESET_ALL
        return infos_str

    @staticmethod
    def format_str_with_color(text: str, color: str = 'blue') -> str:
        return COLOR_DICT[color] + text + Style.RESET_ALL

    @staticmethod
    def log_to_stdout(message:str, color=None):
        colored_message = COLOR_DICT[color] + message + Style.RESET_ALL
        print(colored_message)


def init_loguru_logger(log_dir="logs") -> "Logger":
    """initialize the loguru logger

    Args:
        log_dir (str, optional): the directory to save the log files. Defaults to "logs".

    Returns:
        Logger: loguru.logger

    Examples::

        logger = init_loguru_logger()
        logger.info("logging to main log")
        logger.bind(custom=True).debug("logging to custom log")

        # in other file, can directly import logger
        from loguru import logger
        logger.info("xxx")
        
    """
    os.makedirs(log_dir, exist_ok=True)
    
    logger.remove()
    logger.add(
        f"{log_dir}/custom_debug.log",
        rotation="10 MB",
        compression="zip",
        level="DEBUG",
        filter=lambda record: "custom" in record["extra"],
    )
    logger.add(f"{log_dir}/app.log", rotation="10 MB", compression="zip", level="INFO")
    logger.add(sys.stdout, level="INFO")
    return logger



if __name__ == '__main__':
    infos = dict(a=1223, b="ss")
    infos = {
        'name': 'Alice',
        'age': 30,
        'hobbies': ['reading', 'cycling', 'hiking'],
        'education': {
            'undergraduate': 'Computer Science',
            'graduate': 'Data Science'
        },
        "infos": "This is a string that needs to be highlighted with borders.\nAnother line. "
    }
    # infos = "This is a string that needs to be highlighted with borders.\nAnother line. "
    print(LogUtils.format_infos_with_tabulate(infos))
    print(LogUtils.format_infos_with_pprint(infos))
    print()

