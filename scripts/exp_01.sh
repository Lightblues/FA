# session simulation for PDL
cd /work/huabu/src/

MODE=pdl # react pdl
MODEL=claude-3-5-sonnet-20240620 #claude-3-haiku-20240307 # Qwen2-72B
datasets=("PDL" "SGD" "STAR")

for dataset in "${datasets[@]}"; do
    echo ">> running pdl-${MODE} on dataset: ${dataset}"
    exp_version=${dataset,,}_pdl-${MODE}_${MODEL}
    
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
        --simulate-num-persona=2 \
        --bot-llm-name=${MODEL} \
        --bot-mode=${bot_mode} --bot-template-fn=${bot_template_fn}
done
# --simulate-force-rerun