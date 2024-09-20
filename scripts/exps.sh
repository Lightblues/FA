cd src
python run_baseline_eval.py --config=default.yaml --exp-version=240919_01 --workflow-dataset=PDL --workflow-type=flowchart


python run_baseline_eval.py --config=default.yaml --exp-version=pdl_flowchart_v0 --workflow-dataset=PDL --workflow-type=flowchart
python run_baseline_eval.py --config=default.yaml --exp-version=pdl_code --workflow-dataset=PDL --workflow-type=code
python run_baseline_eval.py --config=default.yaml --exp-version=pdl_text --workflow-dataset=PDL --workflow-type=text
python run_baseline_eval.py --config=default.yaml --exp-version=pdl_pdl_v0 --workflow-dataset=PDL --workflow-type=pdl

ID=0920
python run_baseline_eval.py --config=default.yaml --exp-version=star_flowchart_${ID} --workflow-dataset=STAR --workflow-type=flowchart --simulate-num-persona=1
python run_baseline_eval.py --config=default.yaml --exp-version=star_code_${ID} --workflow-dataset=STAR --workflow-type=code --simulate-num-persona=1
python run_baseline_eval.py --config=default.yaml --exp-version=star_text_${ID} --workflow-dataset=STAR --workflow-type=text --simulate-num-persona=1
