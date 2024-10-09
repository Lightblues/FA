# turn exp for other models
cd /work/huabu/src/

workflow_types=("text" "code" "flowchart")
MODEL=claude-3-5-sonnet-20240620 #claude-3-haiku-20240307 #Qwen2-72B # gpt-4o
dataset=SGD # PDL SGD STAR

for wt in "${workflow_types[@]}"; do
    echo ">> running ${MODEL} on dataset: ${dataset} with workflow_type: ${wt}"
    exp_version=turn_${dataset,,}_${wt}_${MODEL}  # prefix = 'turn_'

    bot_mode="react_bot"
    bot_template_fn="flowagent/bot_flowbench.jinja"

    python run_flowagent_exp.py --config=default.yaml --exp-version=${exp_version} --exp-mode=turn \
        --workflow-dataset=${dataset} --workflow-type=${wt} \
        --simulate-num-persona=2 \
        --bot-llm-name=${MODEL} \
        --bot-mode=${bot_mode} --bot-template-fn=${bot_template_fn}
done
