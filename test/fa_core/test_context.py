from fa_core.agents.envs.base_env import StatusForPrompt

status_for_prompt = StatusForPrompt()
print(status_for_prompt.to_str())

status_for_prompt.api_duplication_controller = "api duplication error"
print(status_for_prompt.to_str())

print()
