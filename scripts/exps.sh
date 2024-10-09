cd src

# =======================================================================================================================
# CLI conversation
python run_flowagent.py --mode=conv \
    --config=default.yaml --exp-version=default --exp-mode=turn \
    --workflow-type=text --workflow-id=000 \
    --user-mode=llm_profile --user-llm-name=gpt-4o --user-profile-id=0 \
    --bot-mode=react_bot --bot-llm-name=gpt-4o \
    --api-mode=llm --api-llm-name=gpt-4o \
    --user-template-fn=baselines/user_llm.jinja --bot-template-fn=baselines/flowbench.jinja \
    --conversation-turn-limit=20 --log-utterence-time --log-to-db

# run a single Judge
python run_flowagent.py --mode=eval \
    --config=default.yaml --exp-version=default \
    --workflow-type=text \
    --user-mode=llm_profile --user-llm-name=gpt-4o \
    --bot-mode=react_bot --bot-llm-name=gpt-4o \
    --api-mode=llm --api-llm-name=gpt-4o \
    --user-template-fn=baselines/user_llm.jinja --bot-template-fn=baselines/flowbench.jinja \
    --conversation-turn-limit=20 --log-utterence-time --log-to-db

# run an experiment
python run_flowagent.py --model=exp \
    --config=default.yaml --exp-version=default \
    --workflow-type=text \
    --user-mode=llm_profile --user-llm-name=gpt-4o \
    --bot-mode=react_bot --bot-llm-name=gpt-4o \
    --api-mode=llm --api-llm-name=gpt-4o \
    --user-template-fn=baselines/user_llm.jinja --bot-template-fn=baselines/flowbench.jinja \
    --conversation-turn-limit=20 --log-utterence-time --log-to-db

# =======================================================================================================================
ID=0920 # star_flowchart_0920
ID=0923
python run_flowagent_exp.py --config=default.yaml --exp-version=star_flowchart_${ID} --workflow-dataset=STAR --workflow-type=flowchart --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=star_code_${ID} --workflow-dataset=STAR --workflow-type=code --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=star_text_${ID} --workflow-dataset=STAR --workflow-type=text --simulate-num-persona=1

python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_pdl_${ID} --workflow-dataset=PDL --workflow-type=pdl --simulate-num-persona=1 \
    --bot-mode=pdl_bot --bot-template-fn=flowagent/bot_pdl.jinja
python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_flowchart_${ID} --workflow-dataset=PDL --workflow-type=flowchart --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_code_${ID} --workflow-dataset=PDL --workflow-type=code --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_text_${ID} --workflow-dataset=PDL --workflow-type=text --simulate-num-persona=1

python run_flowagent_exp.py --config=default.yaml --exp-version=sgd_pdl_${ID} --workflow-dataset=SGD --workflow-type=pdl --simulate-num-persona=1 \
    --bot-mode=pdl_bot --bot-template-fn=flowagent/bot_pdl.jinja
python run_flowagent_exp.py --config=default.yaml --exp-version=sgd_flowchart_${ID} --workflow-dataset=SGD --workflow-type=flowchart --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=sgd_code_${ID} --workflow-dataset=SGD --workflow-type=code --simulate-num-persona=1
python run_flowagent_exp.py --config=default.yaml --exp-version=sgd_text_${ID} --workflow-dataset=SGD --workflow-type=text --simulate-num-persona=1