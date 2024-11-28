#!/bin/bash

cd /cephp/huabu_online/src
streamlit run run_flowagent_ui.py -- --config=ui_deploy.yaml
# streamlit run run_flowagent_ui.py --server.port=8001  -- --config=ui_deploy.yaml 

# poetry run # 通过poetry执行的时候, 这个传入方式有问题?? -- --config=default.yaml
