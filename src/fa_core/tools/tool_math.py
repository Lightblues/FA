"""
from @ian /cq8/ianxxu/chatchat/_TaskPlan/UI/v2.7_demo/tools/math_tool.py
https://docs.sympy.org/latest/tutorials/intro-tutorial/index.html
"""

from sympy import sympify
from .register import register_tool


@register_tool()
def calculator(question: str) -> str:
    """Use Python's SymPy package to calculate simple math expressions

    Args:
        question (str): the math expression to be calculated

    Returns:
        str: the result of the math expression
    """
    try:
        # https://docs.sympy.org/latest/tutorials/intro-tutorial/simplification.html
        return str(float(sympify(question)))
    except Exception as e:
        return str(e)
