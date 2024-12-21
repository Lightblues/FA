"""
@241221
- [x] finish overall convertion procedure!
- [x] add hunyuan results
"""

from concurrent.futures import ThreadPoolExecutor

import tqdm
import yaml
import json
from data_utils.converter.workflow_pdl_converter import WorkflowPDLConverter

data_version = "v241127"
export_version = "export-1732628942"

# llm_name="gpt-4o-mini"
# output_version = "20241221_4omini"
# llm_name="hunyuan-turbo"
# output_version = "20241221_hyturbo"
llm_name = "gpt-4o"
output_version = "20241221_4o"

workflow_ids = ["000", "001", "002", "004", "006", "007"]
max_workers = 10


def convert():
    converter = WorkflowPDLConverter(llm_name=llm_name, data_version=data_version, export_version=export_version)
    dm = converter.data_manager

    odir = dm.DIR_dataset / dm.data_version / f"pdl_converted_{output_version}"
    odir_tools = odir / "tools"
    odir_pdl = odir / "pdl"
    odir_debug = odir / "debug"
    for d in [odir, odir_tools, odir_pdl, odir_debug]:
        d.mkdir(parents=True, exist_ok=True)

    with open(odir / "task_infos.json", "w") as f:
        task_infos = dm.get_task_infos()
        task_infos = {k: v for k, v in task_infos.items() if k in workflow_ids}
        out = {
            "version": dm.data_version,
            "task_infos": task_infos,
        }
        f.write(json.dumps(out, ensure_ascii=False, indent=4))

    def process_workflow(workflow_id):
        res = converter.convert(workflow_id)
        with open(odir_pdl / f"{workflow_id}.yaml", "w") as f:
            f.write(res["pdl"].to_str())
        with open(odir_tools / f"{workflow_id}.yaml", "w") as f:
            tools = [tool.model_dump(exclude_none=True, exclude_unset=True) for tool in res["tools"]]
            f.write(yaml.dump(tools, sort_keys=False, allow_unicode=True))

        with open(odir_debug / f"{workflow_id}_llm_prompt.txt", "w") as f:
            f.write(res["llm_prompt"])
        with open(odir_debug / f"{workflow_id}_llm_response.txt", "w") as f:
            f.write(res["llm_response"])
        return workflow_id

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(tqdm.tqdm(executor.map(process_workflow, workflow_ids), total=len(workflow_ids)))


if __name__ == "__main__":
    convert()
