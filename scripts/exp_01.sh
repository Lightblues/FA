cd /work/huabu/src/


# ID=0924
# python run_flowagent_exp.py --config=default.yaml --exp-version=pdl_pdl_${ID} --workflow-dataset=PDL --workflow-type=pdl --simulate-num-persona=1 \
#     --bot-mode=pdl_bot --bot-template-fn=flowagent/bot_pdl.jinja


ID=0924_03
MODE=react # pdl
MODEL=gpt-4o-mini
datasets=("PDL" "SGD" "STAR")

for dataset in "${datasets[@]}"; do
    echo ">> running dataset: ${dataset}"
    exp_version=${dataset,,}_pdl_${ID}
    if [ "$MODE" == "pdl" ]; then
        bot_mode="pdl_bot"
        bot_template_fn="flowagent/bot_pdl.jinja"
    elif [ "$MODE" == "react" ]; then
        bot_mode="react_bot"
        bot_template_fn="flowagent/bot_flowbench.jinja"
    else
        echo "Unknown MODE: $MODE"
        exit 1
    fi

    python run_flowagent_exp.py --config=default.yaml --exp-version=${exp_version} --workflow-dataset=${dataset} --workflow-type=pdl \
        --simulate-num-persona=1 \
        --bot-llm-name=${MODEL} \
        --bot-mode=${bot_mode} --bot-template-fn=${bot_template_fn}
done
