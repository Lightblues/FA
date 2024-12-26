from fa_eval.data import FixedQueries

data = {
    "workflow_dataset": "v241127",
    "workflow_id": "000",  # 挂号
    "eval_session_id": "d129f53b-e150-4076-82fe-cdc9516067ef",
    "eval_description": "在北大第一医院没有儿科的情况下拒绝了其他医院的挂号",
    "user_queries": [
        "身份证号310105199810084207，麻烦帮忙挂号",
        "北大第一医院",
        "...",
    ],
}

fixed_queries = FixedQueries(**data)

print(fixed_queries)
print()
