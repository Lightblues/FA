import tqdm
from data_utils.converter.workflow_pdl_converter import WorkflowPDLConverter
from concurrent.futures import ThreadPoolExecutor

converter = WorkflowPDLConverter(llm_name='gpt-4o-mini')
dm = converter.data_manager
version = "20241217"
odir = dm.DIR_data / dm.data_version / f"pdl_converted_{version}"; odir.mkdir(parents=True, exist_ok=True)

def process_workflow(workflow_id):
    if (odir / workflow_id / "llm_response.txt").exists(): return workflow_id
    res = converter.convert(workflow_id)
    oodir = odir / workflow_id
    oodir.mkdir(parents=True, exist_ok=True)
    
    with open(oodir / "pdl.yaml", "w") as f: f.write(str(res["pdl"]))
    with open(oodir / "llm_prompt.txt", "w") as f: f.write(res["llm_prompt"])
    with open(oodir / "llm_response.txt", "w") as f: f.write(res["llm_response"])
    return workflow_id

workflow_ids = ["000", "001", "002", "004", "006", "007"]
with ThreadPoolExecutor(max_workers=10) as executor:
    list(tqdm.tqdm(
        executor.map(process_workflow, workflow_ids),
        total=len(workflow_ids)
    ))
