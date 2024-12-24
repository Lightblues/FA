from typing import Dict

from pydantic import BaseModel


class ToolCall(BaseModel):
    name: str
    params: Dict

    @classmethod
    def from_dict(cls, d: Dict):
        if "name" not in d:
            data = {
                "name": d.get("API"),
                "params": {i["name"]: i["value"] for i in d["params"]},
            }
        else:
            data = d
        return cls(**data)
