
LOCAL_DIR=/work/huabu
COS_DIR=LLM_data/easonsshi/huabu

# fn=data/openagi_data.zip
fn=data/travel_database.zip
coscmd upload ${LOCAL_DIR}/${fn} ${COS_DIR}/${fn}
coscmd download ${COS_DIR}/${fn} ${LOCAL_DIR}/${fn}

coscmd download -r ianxxu/pretrained_models/LLaMa-2-7B/ ./pretrained_models


python -c "import torch; print(torch.cuda.is_available())"



