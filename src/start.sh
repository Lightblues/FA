ROOT=/apdcephfs_cq8/share_2992827/shennong_5/easonsshi
export PYTHONPATH=${ROOT}/huabu/src:${ROOT}/easonsi/src/
PROJECT_DIR=${ROOT}/huabu

# workflow_name="006-同程开发票"
# workflow_name="011-银行订单查询"
# workflow_name="013-查询工作流程"
# workflow_name=006-同程开发票
workflow_name=010-进口运费查询
workflow_name=011-银行订单查询
# model_name="qwen2_72B"
model_name="gpt-4o"

cd ${PROJECT_DIR}/data/
fn_api_log="apis_log/${workflow_name}.log"
echo "Start ${workflow_name}! Log file: ${fn_api_log}"
python -u v240628/apis_v01/${workflow_name}.py > ${fn_api_log} 2>&1 &

cd ${PROJECT_DIR}/src/
python main.py --workflow_name ${workflow_name} 

