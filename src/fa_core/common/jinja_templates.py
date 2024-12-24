from pathlib import Path
from typing import Union

import jinja2


env = None


def jinja_init(rootdir: Union[str, Path]):
    """initialize the jinja2 environment

    Args:
        rootdir (Union[str, Path]): the root directory of the jinja2 templates

    Examples::

        jinja_init(Path(__file__).parent / "templates")
        jinja_render("name.jinja", **kwargs)
    """
    if isinstance(rootdir, Path):
        rootdir = str(rootdir)
    global env
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(rootdir), autoescape=jinja2.select_autoescape())
    env.trim_blocks = True


def jinja_render(template, **kwargs):
    """render the jinja2 template. remind to call ``jinja_init`` first"""
    global env
    return env.get_template(template).render(**kwargs)


# default set rootdir to current dir
jinja_init(Path(__file__).parent / "templates")
