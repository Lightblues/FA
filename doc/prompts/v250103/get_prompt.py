"""
This script is used to generate the prompt for the workflow.

Usage::

    python get_prompt.py --workflow_dataset v241127 --workflow_id 000 --conversation "[USER] 挂301的口腔科" --current_state "2025-01-02 20:13:55 (Thursday)"
    python get_prompt.py --workflow_dataset v241127_converted_ruled --workflow_id 007 --conversation "conversation_Congo" --current_state "current_state_Congo" --output_fn "tmp.md"

@250103 implement the first version.
- see doc https://doc.weixin.qq.com/doc/w3_AcMATAZtAPIQXSbobpAScq6BqSjg0
"""

import pathlib
import jinja2
import argparse

import sample_data
from fa_core.data import FAWorkflow, PDL, ExtToolSpec
from fa_core.common import json_line, LogUtils
from fa_core.agents.bots.bot_tools import tool_response, tool_switch_main

_DIR = pathlib.Path(__file__).parent


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow_dataset", type=str, default="v241127")
    parser.add_argument("--workflow_id", type=str, default="000")
    parser.add_argument("--conversation", type=str, default=sample_data.conversation)
    parser.add_argument("--current_state", type=str, default=sample_data.current_state)
    parser.add_argument("--output_fn", type=str, default=None)
    args = parser.parse_args()
    return args


def format_pdl(pdl: PDL) -> str:
    """Format the pdl into a string using XML formatting.

    Output format::

        <Desc>
        ...
        </Desc>
        <SLOT>
        ...
        </SLOT>
        <ANSWER>
        ...
        </ANSWER>
        <Procedure>
        ...
        </Procedure>
    """
    sections = []
    sections.append(f"<Desc>\n{pdl.Desc}\n</Desc>")
    slot_lines = [json_line(slot.model_dump()) for slot in pdl.SLOTs]
    sections.append("<SLOT>\n" + "\n".join(slot_lines) + "\n</SLOT>")
    answer_lines = [json_line(answer.model_dump()) for answer in pdl.ANSWERs]
    sections.append("<ANSWER>\n" + "\n".join(answer_lines) + "\n</ANSWER>")
    sections.append(f"<Procedure>\n{pdl.Procedure}\n</Procedure>")
    return "\n".join(sections)


def format_toolbox(tools: list[ExtToolSpec]) -> str:
    """Format the tools into lines of json.

    Sample line::

        {"name": "check_hospital_exist", "description": "Check if the hospital exists", "parameters": <json schema>, "required": ["hos_name"]}
    """
    tool_specs = [tool.to_tool_spec() for tool in tools] + [tool_response.function, tool_switch_main.function]
    return "\n".join([json_line(tool.model_dump()) for tool in tool_specs])


def get_prompt(args: argparse.Namespace) -> str:
    workflow = FAWorkflow(workflow_dataset=args.workflow_dataset, workflow_id=args.workflow_id)
    template = jinja2.Template(open(_DIR / "template.jinja").read())
    _pdl = format_pdl(workflow.pdl)
    _toolbox = format_toolbox(workflow.toolbox)
    # try parse the conversation and current_state from sample_data
    if args.conversation in sample_data.__dict__:
        args.conversation = sample_data.__dict__[args.conversation]
    if args.current_state in sample_data.__dict__:
        args.current_state = sample_data.__dict__[args.current_state]
    prompt = template.render(
        workflow_name=workflow.name,
        PDL=_pdl,
        api_infos=_toolbox,
        conversation=args.conversation,
        current_state=args.current_state,
    )
    if args.output_fn:
        with open(_DIR / args.output_fn, "w") as f:
            f.write(prompt)
    return prompt


if __name__ == "__main__":
    args = parse_args()
    prompt = get_prompt(args)
    print(LogUtils.format_infos_with_tabulate(prompt))
