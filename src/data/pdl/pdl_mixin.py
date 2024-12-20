from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PDLMixin(BaseModel):
    invalid_apis: Dict[str, Dict] = Field(default_factory=dict)  # {name: {api_name, [invalid_reason]}}
    current_api_status: List[str] = Field(default_factory=list)  # strings that descripts api status
    status_for_prompt: Dict[str, str] = Field(default_factory=dict)

    def add_invalid_apis(self, api_list: List[Dict]):
        for api in api_list:
            if api["api_name"] in self.invalid_apis:
                self.invalid_apis[api["api_name"]]["invalid_reason"].extend(api["invalid_reason"])
            else:
                self.invalid_apis[api["api_name"]] = api

    def reset_invalid_api(self):
        if self.invalid_apis:
            self.invalid_apis.clear()

    def get_valid_apis(self):
        return [api for api in self.APIs if api.name not in self.invalid_apis]

    def add_current_api_status(self, status):
        self.current_api_status.append(status)

    def reset_api_status(self):
        self.current_api_status.clear()
