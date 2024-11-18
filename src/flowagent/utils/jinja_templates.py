import jinja2
from pathlib import Path
from typing import *

env = None

def jinja_init(rootdir: Union[str, Path]):
    if isinstance(rootdir, Path):
        rootdir = str(rootdir)
    global env
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(rootdir),
        autoescape=jinja2.select_autoescape()
    )
    env.trim_blocks = True


def jinja_render(template, **kwargs):
    global env
    return env.get_template(template).render(**kwargs)

# default set rootdir to current dir
jinja_init(Path(__file__).parent / "templates")
