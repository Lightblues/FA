from common import Config
from fa.bots.react_bot import ReactBot


if __name__ == "__main__":
    cfg = Config()
    bot = ReactBot(cfg=cfg)
    print(bot)
