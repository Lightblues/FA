import sys
from colorama import init, Fore, Style

class BaseLogger:
    def __init__(self):
        # Initialize colorama
        init(autoreset=True)

    def log_to_stdout(self, message, color=None):
        color_dict = {
            'gray': Fore.LIGHTBLACK_EX,
            'orange': Fore.LIGHTYELLOW_EX,
            'red': Fore.RED,
            'green': Fore.GREEN,
            'blue': Fore.BLUE,
            'yellow': Fore.YELLOW,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE
        }

        if color in color_dict:
            colored_message = color_dict[color] + message + Style.RESET_ALL
        else:
            colored_message = message

        print(colored_message)

# Example usage
if __name__ == "__main__":
    logger = BaseLogger()
    logger.log_to_stdout("This is a gray message", "gray")
    logger.log_to_stdout("This is an orange message", "orange")
    logger.log_to_stdout("This is a default color message")
