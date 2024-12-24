
Environment variables:
- `LOCAL_MODELS_CONFIG_PATH`: the path to the local models config file (OpenAI client)
- `LOCAL_MODELS_INFO_PATH`: local model registry file (inner only!)

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
# 3.1 run backend & frontend
python run_demo_backend.py --config=dev.yaml --port=8101 --reload
streamlit run run_demo_frontend.py --server.port 8502 -- --config=dev.yaml --page_default_index=0
# ... interct in the UI!

# or, can also install the package
pip install -e .
```
