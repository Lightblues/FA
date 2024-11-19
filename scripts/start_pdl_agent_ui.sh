#!/bin/bash

cd /work/huabu/src
# poetry run # 通过poetry执行的时候, 这个传入方式有问题?? -- --config=default.yaml
# streamlit run run_flowagent_ui_demo.py --server.port=8001  -- --config=ui_deploy.yaml 
# streamlit run run_flowagent_ui_demo.py --server.port=18801  -- --config=ui_deploy.yaml
streamlit run run_flowagent_ui_demo.py --server.port=18801 --server.fileWatcherType=watchdog -- --config=ui_dev.yaml

