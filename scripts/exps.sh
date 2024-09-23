cd src
python run_flowagent_exp.py --config=default.yaml --exp-version=240919_01 --workflow-dataset=PDL --workflow-type=flowchart

python run_flowagent_cli.py --config=default.yaml --exp-version=pdl_pdl_${ID} --workflow-dataset=PDL --workflow-type=pdl \
    --bot-mode=pdl_bot --bot-template-fn=flowagent/pdl.jinja


# =======================================================================================================================
ID=0920 # star_flowchart_0920
ID=0923
python run_flowagent_exp.py --config=default.yaml --exp-version=star_flowchart_${ID} --workflow-dataset=STAR --workflow-type=flowchart --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=star_code_${ID} --workflow-dataset=STAR --workflow-type=code --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=star_text_${ID} --workflow-dataset=STAR --workflow-type=text --simulate-num-persona=1

python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_pdl_${ID} --workflow-dataset=PDL --workflow-type=pdl --simulate-num-persona=1 \
    --bot-mode=pdl_bot --bot-template-fn=flowagent/pdl.jinja
python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_flowchart_${ID} --workflow-dataset=PDL --workflow-type=flowchart --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_code_${ID} --workflow-dataset=PDL --workflow-type=code --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_text_${ID} --workflow-dataset=PDL --workflow-type=text --simulate-num-persona=1

python run_flowagent_exp.py --config=default.yaml --exp-version=sgd_pdl_${ID} --workflow-dataset=SGD --workflow-type=pdl --simulate-num-persona=1 \
    --bot-mode=pdl_bot --bot-template-fn=flowagent/pdl.jinja
python run_flowagent_exp.py --config=default.yaml --exp-version=sgd_flowchart_${ID} --workflow-dataset=SGD --workflow-type=flowchart --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=sgd_code_${ID} --workflow-dataset=SGD --workflow-type=code --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=sgd_text_${ID} --workflow-dataset=SGD --workflow-type=text --simulate-num-persona=1