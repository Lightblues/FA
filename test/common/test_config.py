from fa_core.common.configs import Config


def test_config():
    cfg = Config.from_yaml("customized.yaml")
    print(cfg)
    print()


if __name__ == "__main__":
    test_config()
