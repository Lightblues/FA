import io
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field


class CoreBlock(BaseModel):
    name: str
    instruction: str
    type: str
    branch: Dict[str, Union[str, "CoreBlock"]] = Field(default_factory=dict)

    @classmethod
    def create(cls, des: str) -> "CoreBlock":
        """
        Create a CoreBlock from description string.

        des format: <name>:::<type>:::<instruction>:::<branch>
        <type>: process or decision or terminal
        <branch>: <key1>::<value1>::<key2>::<value2>::...
        Example: Step 1:::decision:::Check whether every models in the generated to-do list is in the provided models:::Yes::step 5::No::step 3
        """
        structured_info = cls._parser(des)
        return cls(
            name=structured_info["name"].lower(),
            instruction=structured_info["instruction"],
            type=structured_info["type"].lower(),
            branch=structured_info["branch"],
        )

    @staticmethod
    def _parser(des: str) -> Dict[str, Any]:
        """
        Parse the block description into structured information.

        Args:
            des: the description of the block.

        Returns:
            structured_info: Dict containing name, type, instruction, and branch info
        """
        structured_info = dict()
        info = [component.strip() for component in des.split(":::")]
        structured_info["name"] = info[0]

        # Check whether type info is correct
        if info[1].lower() not in ["process", "decision", "terminal"]:
            raise ValueError("The type is not in [process, decision, terminal]")

        structured_info["type"] = info[1]
        structured_info["instruction"] = info[2]
        structured_info["branch"] = dict()
        branch_info = [branch.strip() for branch in info[3].split("::")]
        num = len(branch_info) // 2
        for i in range(num):
            structured_info["branch"][branch_info[2 * i].lower()] = branch_info[2 * i + 1].lower()

        return structured_info

    def get_instruction(self) -> str:
        return self.instruction

    def __str__(self) -> str:
        branch_str = ""
        for key, value in self.branch.items():
            if isinstance(value, str):
                branch_str += f"if {key}, then go to {value}. "
            else:
                branch_str += f"if {key}, then go to {value.name}. "

        return f"{self.name}, the type is {self.type}, the instruction is {self.instruction} {branch_str}\n"


class CoreFlow(BaseModel):
    block_dict: Dict[str, CoreBlock] = Field(default_factory=dict)
    header: Optional[CoreBlock] = None

    @classmethod
    def create(cls, flow_str: str) -> "CoreFlow":
        """
        Construct the flow based on the descriptions from flow string

        Args:
            flow_str (str): string containing the flow instructions.
        """
        self = cls()  # Create instance with default values

        flow_lines = flow_str.strip().split("\n")
        for row in flow_lines:
            step_block = CoreBlock.create(row)
            self.block_dict[step_block.name] = step_block
            if self.header is None:
                self.header = step_block
        self.connect_blocks()
        return self

    @classmethod
    def load_from_file(cls, flow_file: str) -> "CoreFlow":
        with io.open(flow_file, "r", encoding="utf-8") as f:
            flow_str = f.read()
        return cls.create(flow_str)

    def connect_blocks(self) -> None:
        """Connect blocks"""
        for key, value in self.block_dict.items():
            try:
                for branch_condition, branch_block in value.branch.items():
                    value.branch[branch_condition] = self.block_dict[branch_block]
            except Exception as e:
                raise Exception("Error when connecting blocks in flow")

    def __str__(self) -> str:
        """Return the flow information as string."""
        flow_str = ""
        for key, value in self.block_dict.items():
            flow_str += value.__str__()
        return flow_str
