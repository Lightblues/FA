import pytest
from fa_core.common import Config


@pytest.fixture
def config_default():
    return Config.from_yaml("default.yaml")
