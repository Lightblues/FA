from ...data import APIOutput, BotOutput, Role
from .llm_simulated_tool import LLMSimulatedTool


class CoREAPIHandler(LLMSimulatedTool):
    api_template_fn: str = "flowagent/api_llm.jinja"
    names = ["core", "CoREAPIHandler"]

    def process(self, apicalling_info: BotOutput, *args, **kwargs) -> APIOutput:
        # special jump process!
        if apicalling_info.action == "binary_choice":
            self.conv.add_message("<jump> success", role=Role.SYSTEM)
            return APIOutput(apicalling_info.action, apicalling_info.action_input, "success", 200)
        return super().process(apicalling_info, *args, **kwargs)
