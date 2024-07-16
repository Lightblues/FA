## TODOs

- [ ] Generate API data automatically
- [x] When pass "--api_mode=vanilla", select and start the API server automatically
- [x] Auto evaluation: `user, api` agent
- [ ] 

## datamodel

```python
# see [engine_v1/datamodel]
class BaseAPIHandler:
    def process_query(self, conversation:Conversation, api_name: str, api_params: Dict) -> str:
        """ 给定上下文和当前的API请求, 返回API的响应 """

```


## run

相关路径
- huabu PDL: `data/v240628/huabu_step3`
- conversation logs: `data/v240628/engine_v1_log/<data>/<time>.log`
- prompts: `src/utils/templates`

```sh
PROJECT_PATH=/apdcephfs_cq8/share_2992827/shennong_5/easonsshi/huabu
cd ${PROJECT_PATH}/src

# 运行交互, 在交互的时候参见 huabu PDL 数据
python main.py --model_name qwen2_72B --api_mode manual --template_fn query_PDL_v01.jinja --workflow_name 005  # workflow_name 即画布名称/ID, 见 huabu PDL 路径
```

