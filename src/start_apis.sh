ROOT=/apdcephfs_cq8/share_2992827/shennong_5/easonsshi
export PYTHONPATH=${ROOT}/huabu/src:${ROOT}/easonsi/src/

python -u apis/011.py

# curl -X 'POST' \
#   'http://localhost:8000/query_by_order_id' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "order_id": "ORD123"
# }'
