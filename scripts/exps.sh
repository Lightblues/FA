cd src
python run_baseline_eval.py --config=default.yaml --exp-version=240819_01 --workflow-dataset=PDL --workflow-type=flowchart

python run_baseline_eval.py --config=default.yaml --exp-version=pdl_flowchart --workflow-dataset=PDL --workflow-type=flowchart
python run_baseline_eval.py --config=default.yaml --exp-version=pdl_code --workflow-dataset=PDL --workflow-type=code
python run_baseline_eval.py --config=default.yaml --exp-version=pdl_text --workflow-dataset=PDL --workflow-type=text

