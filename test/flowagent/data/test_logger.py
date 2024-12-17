# %%
from flowagent.data import LogUtils


data = f"{'afff'*201}\n" * 20
s = LogUtils.format_infos_with_pprint(data)
print(s)
# %%
import pprint


pprint.pformat(data)
# %%
import textwrap


def create_boxed_text(text, width: int):
    if not isinstance(text, str):
        text = str(text)

    # Wrap the text to the specified width
    wrapped_text = textwrap.fill(text, width=width)

    lines = wrapped_text.split("\n")
    box_width = max(len(line) for line in lines) + 2
    top_border = "+" + "-" * (box_width + 2) + "+"
    bottom_border = "+" + "-" * (box_width + 2) + "+"
    boxed_text = top_border + "\n"
    for line in lines:
        boxed_text += "| " + line.ljust(box_width) + " |\n"
    boxed_text += bottom_border

    return boxed_text


# Example usage
text = "This is a long string that needs to be wrapped within a certain width and placed inside a box.\n" * 3
_text = {
    "a": "This is a long string that needs to be wrapped within a certain width and placed inside a box.\n" * 3,
    "b": "This is a long string that needs to be wrapped within a certain width and placed inside a box.",
}
width = 70
boxed_text = create_boxed_text(text, width)
print(boxed_text)

# %%
print(textwrap.fill(text, width=70, replace_whitespace=False))
# %%
