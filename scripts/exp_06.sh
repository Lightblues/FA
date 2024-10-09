# session OOW simulateion for other models
cd /work/huabu/src/

workflow_types=("text" "code" "flowchart")
MODEL=Qwen2-72B # gpt-4o-mini
dataset=SGD # PDL STAR

for wt in "${workflow_types[@]}"; do
    echo ">> [session OOW] running ${MODEL} on dataset: ${dataset} with workflow_type: ${wt}"
    exp_version=sessionOOW_${dataset,,}_${wt}_${MODEL}

    bot_mode="react_bot"

    python run_flowagent_exp.py --config=default.yaml --exp-version=${exp_version} --workflow-dataset=${dataset} --workflow-type=${wt} \
        --simulate-num-persona=2 \
        --bot-llm-name=${MODEL} \
        --bot-mode=${bot_mode} --user-mode="llm_oow"
done
