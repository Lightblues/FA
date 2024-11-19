# session OOW simulation for CORE
cd /work/huabu/src/

MODEL=gpt-4o-mini # Qwen2-72B
datasets=("PDL" "SGD" "STAR")
datasets=("PDL")
datasets=("SGD" "STAR")

for dataset in "${datasets[@]}"; do
    echo ">> [session OOW] running core on dataset: ${dataset}"
    exp_version=sessionOOW_${dataset,,}_core_${MODEL}
    python run_flowagent.py --mode="exp" \
        --config=default.yaml --exp-version=${exp_version} --workflow-dataset=${dataset} --workflow-type=pdl \
        --simulate-num-persona=5 \
        --bot-llm-name=${MODEL} \
        --workflow-type="core" --bot-mode="core_bot" --api-mode="core" --user-mode="llm_oow"
done
