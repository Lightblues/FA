ROOT=/apdcephfs_cq8/share_2992827/shennong_5/easonsshi
export PYTHONPATH=${ROOT}/huabu/src:${ROOT}/easonsi/src/
PROJECT_DIR=${ROOT}/huabu

# 
python run_cli_v2.py \
    --model_name=gpt-4o --template_fn=query_PDL.jinja --api_mode=v01 \
    --workflow_dir=huabu_step3 --workflow_name=000 \


# ------------------ archived version ------------------
# workflow_name="006-同程开发票"
workflow_name=010-进口运费查询
model_name="qwen2_72B"
# model_name="gpt-4o"

cd ${PROJECT_DIR}/data/
fn_api_log="apis_log/${workflow_name}.log"
echo "Start ${workflow_name}! Log file: ${fn_api_log}"
python -u v240628/apis_v01/${workflow_name}.py > ${fn_api_log} 2>&1 &

cd ${PROJECT_DIR}/src/
python main.py --workflow_name ${workflow_name} 

