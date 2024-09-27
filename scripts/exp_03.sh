# turn exp for PDL
cd /work/huabu/src/

MODE=pdl # react pdl
MODEL=Qwen2-72B # gpt-3.5-turbo gpt-4o claude-3-sonnet-20240229 Qwen2-72B
datasets=("PDL" "SGD" "STAR")

for dataset in "${datasets[@]}"; do
    echo ">> running pdl-${MODE} on dataset: ${dataset}"
    exp_version=turn_${dataset,,}_pdl-${MODE}_${MODEL}
    
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

    python run_flowagent_exp.py --config=default.yaml --exp-version=${exp_version} --exp-mode=turn \
        --workflow-dataset=${dataset} --workflow-type=pdl \
        --simulate-num-persona=3 \
        --bot-llm-name=${MODEL} \
        --bot-mode=${bot_mode} --bot-template-fn=${bot_template_fn}
done
