cd src
python run_flowagent_exp.py --config=default.yaml --exp-version=240919_01 --workflow-dataset=PDL --workflow-type=flowchart


python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_flowchart_v0 --workflow-dataset=PDL --workflow-type=flowchart
python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_code --workflow-dataset=PDL --workflow-type=code
python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_text --workflow-dataset=PDL --workflow-type=text
python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_pdl_v0 --workflow-dataset=PDL --workflow-type=pdl

ID=0920 # star_flowchart_0920
python run_flowagent_exp.py --config=default.yaml --exp-version=star_flowchart_${ID} --workflow-dataset=STAR --workflow-type=flowchart --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=star_code_${ID} --workflow-dataset=STAR --workflow-type=code --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=star_text_${ID} --workflow-dataset=STAR --workflow-type=text --simulate-num-persona=1


ID=0923
python run_flowagent_exp.py --config=default.yaml --exp-version=sgd_flowchart_${ID} --workflow-dataset=SGD --workflow-type=flowchart --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=sgd_code_${ID} --workflow-dataset=SGD --workflow-type=code --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=sgd_text_${ID} --workflow-dataset=SGD --workflow-type=text --simulate-num-persona=1