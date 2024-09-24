cd /work/huabu/src/


# ID=0924
# # PDL
# python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_pdl_${ID} --workflow-dataset=PDL --workflow-type=pdl --simulate-num-persona=1 \
#     --bot-mode=pdl_bot --bot-template-fn=flowagent/pdl.jinja
# # SGD
# python run_flowagent_exp.py --config=default.yaml --exp-version=sgd_pdl_${ID} --workflow-dataset=SGD --workflow-type=pdl --simulate-num-persona=1 \
#     --bot-mode=pdl_bot --bot-template-fn=flowagent/pdl.jinja
# # STAR
# python run_flowagent_exp.py --config=default.yaml --exp-version=star_pdl_${ID} --workflow-dataset=STAR --workflow-type=pdl --simulate-num-persona=1 \
#     --bot-mode=pdl_bot --bot-template-fn=flowagent/pdl.jinja
#!/bin/bash

ID=0924_01
datasets=("PDL" "SGD" "STAR")

for dataset in "${datasets[@]}"; do
    echo ">> running dataset: ${dataset}"
    exp_version=${dataset,,}_pdl_${ID}
    python run_flowagent_exp.py --config=default.yaml --exp-version=${exp_version} --workflow-dataset=${dataset} --workflow-type=pdl \
        --simulate-num-persona=1 
        # --bot-mode=pdl_bot --bot-template-fn=flowagent/pdl.jinja
done
