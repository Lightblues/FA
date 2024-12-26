from fa_eval.data.data_handler import FAEvalDataHandler

fixed_queries = FAEvalDataHandler.get_eval_fixed_queries("v241127", "快递费用和到达时间是多少")
print(f"Loaded {len(fixed_queries)} fixed queries")
print(fixed_queries)
