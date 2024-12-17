
# How to seperate deployed version and development version?
# fork the repo to /work/huabu_online and run seperatly!

g clone https://github.com/Lightblues/SN_huabu.git /work/huabu_online
cd /work/huabu_online
# soft link data
ln -s /work/huabu/data /work/huabu_online/data

# --- run the server
tmux attach -t huabu # run in tmux

cd /work/huabu_online/scripts
./start_ui.sh


# --- run this repo locally
cd $PROJECT_PATH/src
# 1. backend
python main.py --model_name=gpt-4o
# 2. UI
streamlit run run_flowagent_ui.py --server.port 8501 -- --config=ui_local.yaml

# kill dead streamlit
ps aux | grep 'config=ui_dev.yaml' | grep -v grep | awk '{print $2}' | xargs kill -9
