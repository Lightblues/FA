import os, json, tqdm, itertools, pickle, collections, traceback, datetime, tabulate
from typing import List, Dict, Optional, Tuple
import pandas as pd
import concurrent.futures
from easonsi import utils
from easonsi.llm.openai_client import OpenAIClient, Formater
from utils.jinja_templates import jinja_render
# from engine import _DIRECTORY_MANAGER, LLM_CFG, init_client, PDL, Config, UserProfile
# from simulator import Simulator

from ..main import BaselineController
from ..data.config import Config


def task_simulate(cfg: Config) -> None:
    """ One simulation task
    """
    controller = BaselineController(cfg)
    controller.start_conversation(verbose=False)