
```sh
# 1. clone the repo & data
git clone git@git.woa.com:easonsshi/huabu.git huabu_test && cd huabu_test
# ... transfer `huabu_1127.zip` to `./dataset` & unzip it

# 2. config the env
conda create -n huabu python=3.10 -y && conda activate huabu
# 2.1 install the dependencies with poetry
#   https://github.com/python-poetry/poetry
#   You may need to config `poetry config virtualenvs.create false` first
poetry install      # or you can use pip to install the dependencies, if you like

# 3. run!
cd src/
tmux new/attach -t huabu
# 3.1 run backend
uvicorn backend.main:app --host 0.0.0.0 --port 8100 --reload --reload-dir ./backend
# 3.2 run frontend
streamlit run run_flowagent_ui2.py -- --config=ui_deploy.yaml
# ... interct in the UI! 
```


