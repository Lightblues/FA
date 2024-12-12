import datetime

class PromptUtils:
    @staticmethod
    def get_formated_time() -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S (%A)")

    @staticmethod
    def get_formated_date() -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d")
