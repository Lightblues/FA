# session simulateion for other models
cd /work/huabu/src/

workflow_types=("text" "code" "flowchart")
MODEL=Qwen2-72B # gpt-4o-mini
dataset=STAR # PDL

for wt in "${workflow_types[@]}"; do
    echo ">> running ${MODEL} on dataset: ${dataset} with workflow_type: ${wt}"
    exp_version=${dataset,,}_${wt}_${MODEL}

    bot_mode="react_bot"
    bot_template_fn="flowagent/bot_flowbench.jinja"

    python run_flowagent_exp.py --config=default.yaml --exp-version=${exp_version} --workflow-dataset=${dataset} --workflow-type=${wt} \
        --simulate-num-persona=2 \
        --bot-llm-name=${MODEL} \
        --bot-mode=${bot_mode} --bot-template-fn=${bot_template_fn}
done