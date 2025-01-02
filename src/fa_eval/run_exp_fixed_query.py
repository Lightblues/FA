"""
Usage::

    python -m fa_eval.run_exp_fixed_query --config_fn=exp_01.yaml --eval_dataset=v241127 --exp_version=exp_01

@241226
- [x] Implement basic version
- [x] add `exp_id`

todos:
- [ ] add option to duplicated exp_id (count_documents_by_query)
"""

import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

from fa_core.common import Config, DBUtils, set_log_level
from fa_core.data import FADataManager
from fa_eval.data import FAEvalDataHandler, FixedQueries
from fa_eval.simulators import FixedQuerySimulator

set_log_level("WARNING")


def get_args() -> argparse.Namespace:
    args = argparse.ArgumentParser()
    args.add_argument("--config_fn", type=str, default="exp_01.yaml")
    args.add_argument("--eval_dataset", type=str, default="v241127")
    args.add_argument("--exp_version", type=str, default="exp_241226")

    args.add_argument("--workflow_dataset", type=str, default=None)
    args.add_argument("--backend_url", type=str, default=None)

    args.add_argument("--max_workers", type=int, default=10)
    args.add_argument("--verbose", action="store_true")
    args = args.parse_args()
    return args


def main():
    args = get_args()
    cfg = Config.from_yaml(args.config_fn)
    db_utils = DBUtils(mongo_uri=cfg.db_uri, db_name=cfg.db_name)

    if args.workflow_dataset:
        cfg.workflow_dataset = args.workflow_dataset
    if args.exp_version:
        cfg.exp_version = args.exp_version
    if args.backend_url:
        cfg.backend_url = args.backend_url

    tasks: list[tuple[FixedQuerySimulator, FixedQueries]] = []
    workflow_infos = FADataManager.get_workflow_infos(cfg.workflow_dataset)
    print(f"building tasks for {cfg.workflow_dataset}...")
    for workflow_id, _workflow_info in workflow_infos.items():
        workflow_name = _workflow_info["name"]
        cfg2 = cfg.copy()
        cfg2.workflow_id = workflow_id  # NOTE to overwrite the workflow_id!
        fixed_queries = FAEvalDataHandler.get_eval_fixed_queries(args.eval_dataset, workflow_name)
        print(f"  workflow_name: {workflow_name}, workflow_id: {workflow_id}, fixed_queries: {len(fixed_queries)}")
        for i, fixed_query in enumerate(fixed_queries):
            cfg3 = cfg2.copy()
            cfg3.exp_id = f"{workflow_name}_{i:03d}"
            # check if the exp_id already exists
            if db_utils.count_documents_by_query({"exp_version": cfg3.exp_version, "exp_id": cfg3.exp_id}, collection=cfg.db_collection_single) > 0:
                print(f"  skip {cfg3.exp_id} because it already exists")
                continue
            simulator = FixedQuerySimulator(cfg=cfg3, verbose=args.verbose)
            tasks.append((simulator, fixed_query))
    print(f"... total tasks: {len(tasks)}")

    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        results = list(tqdm(executor.map(lambda task: task[0].run_with_try_catch(task[1]), tasks), total=len(tasks), desc="running tasks"))
    print(f"DONE! {sum(results)} / {len(results)} success!")


if __name__ == "__main__":
    main()
