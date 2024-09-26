cd /work/huabu/src/


# MODE=pdl
MODE=react
MODEL=gpt-4o
# MODEL=gpt-3.5-turbo
# MODEL=claude-3-sonnet-20240229
# MODEL=Qwen2-72B
# datasets=("PDL" "SGD" "STAR")
datasets=("PDL")

for dataset in "${datasets[@]}"; do
    echo ">> running dataset: ${dataset}"
    exp_version=${dataset,,}_pdl_0924_${MODE}_${MODEL}
    
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
