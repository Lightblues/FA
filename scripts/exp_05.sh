# session OOW simulation for PDL
cd /work/huabu/src/

MODE=pdl # react pdl
MODEL=Qwen2-72B
datasets=("PDL" "SGD" "STAR")

for dataset in "${datasets[@]}"; do
    echo ">> [session OOW] running pdl-${MODE} on dataset: ${dataset}"
    exp_version=sessionOOW_${dataset,,}_pdl-${MODE}_${MODEL}
    if [ "$MODE" == "pdl" ]; then
        bot_mode="pdl_bot"
    elif [ "$MODE" == "react" ]; then
        bot_mode="react_bot"
    else
        echo "Unknown MODE: $MODE"
        exit 1
    fi
    
    python run_flowagent_exp.py --config=default.yaml --exp-version=${exp_version} --workflow-dataset=${dataset} --workflow-type=pdl \
        --simulate-num-persona=3 \
        --bot-llm-name=${MODEL} \
        --bot-mode=${bot_mode} --user-mode="llm_oow"
done