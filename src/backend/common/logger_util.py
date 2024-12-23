from loguru import logger


class LoggerUtil:
    def __init__(self):
        self.logger = logger
        self.logger_debug = logger.bind(custom=True)

    def debug_section(self, title: str):
        self.logger_debug.debug(f"\n{title.center(150, '=')}")

    def debug_section_content(self, content: str, subtitle: str = ""):
        if subtitle:
            content = f"\n<<{subtitle}>>\n{content}\n"
        self.logger_debug.debug(f"{content}")


logger_util = LoggerUtil()
