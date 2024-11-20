```python
    def insert_conversation(self, conversation: Conversation):
    def query_messages_by_conversation_id(self, conversation_id: str) -> Conversation:
    
    def insert_config(self, infos: dict):
    def query_config_by_conversation_id(self, conversation_id: str) -> dict:
    def get_most_recent_unique_conversation_ids(self, query={})

    def query_evaluations(self, query: dict = {}, limit: int = 0) -> List[dict]:
    def insert_evaluation(self, eval_result: dict):

    # base_cm
    def query_run_experiments(self, query: dict = {}, limit: int = 0) -> List[dict]:
    def delete_run_experiments(self, query: dict = {}):
```

### 数据存储 (mongo)

1. `conversation_id` 标记一个会话, 关联三张表
2. `exp_version` 标记一组实验, 一个exp_version中的实验包含相同的 workflow_dataset & workflow_type
    1. 因此, `exp_version + workflow_id + user_profile_id` 标记了一个实验中的一次实验
    2. 一个固定的 exp_version 关联其他的参数, fix 下来 (dump config). 

```sh
# config. PK: conversation_id
(exp_version, conversation_id), log_file, <config> (workflow_dataset, workflow_type, workflow_id), ...
# messages. PK: (conversation_id, utterance_id), FK: (conversation_id)
(conversation_id, utterance_id), (role, content), (prompt, llm_response)
# eval FK: (conversation_id)
(conversation_id), judje_model, <eval results>
```
