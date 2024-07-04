ROOT=/apdcephfs_cq8/share_2992827/shennong_5/easonsshi
export PYTHONPATH=${ROOT}/huabu/src:${ROOT}/easonsi/src/

# workflow_name="006-同程开发票"
workflow_name="011-银行订单查询"
python main.py --workflow_name ${workflow_name} 

