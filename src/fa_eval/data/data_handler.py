import json, jsonlines
from functools import cache
from fa_core.data import FADataManager
from .fixed_queries import FixedQueries


class FAEvalDataHandler(FADataManager):
    """DataHandler for eval fixed queries

    Usage::

        fixed_queries = FAEvalDataHandler.get_eval_fixed_queries("v241127", "快递费用和到达时间是多少")
        # see the `task_infos.json`
    """

    @cache
    @staticmethod
    def get_all_eval_task_infos() -> dict:
        fn = FADataManager.DIR_data_eval_fixed_queries / "task_infos.json"
        return json.load(open(fn, "r"))

    @cache
    @staticmethod
    def get_dataset_name_id_map(dataset_name: str) -> dict:
        task_infos = FAEvalDataHandler.get_all_eval_task_infos()
        assert dataset_name in task_infos, f"Dataset name {dataset_name} not found in task_infos ({task_infos.keys()})"
        return {v["name"]: k for k, v in task_infos[dataset_name].items()}

    @cache
    @staticmethod
    def get_eval_fixed_queries(dataset_name: str, workflow_name: str) -> list[FixedQueries]:
        workflow_id = FAEvalDataHandler._check_workflow_id(dataset_name, workflow_name)
        fn = FADataManager.DIR_data_eval_fixed_queries / f"{dataset_name}/{workflow_id}.jsonl"
        data_list = [q for q in jsonlines.open(fn, "r") if q]
        return [FixedQueries(**q) for q in data_list]

    @staticmethod
    def _check_workflow_id(dataset_name: str, workflow_name_or_id: str) -> str:
        dataset_name_id_map = FAEvalDataHandler.get_dataset_name_id_map(dataset_name)
        if workflow_name_or_id in dataset_name_id_map:
            workflow_name_or_id = dataset_name_id_map[workflow_name_or_id]
        else:
            assert workflow_name_or_id in dataset_name_id_map.values(), f"Workflow name {workflow_name_or_id} not found in dataset {dataset_name}"
        return workflow_name_or_id
