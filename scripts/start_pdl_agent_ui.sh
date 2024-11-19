#!/bin/bash

cd /mnt/huabu/src
# poetry run # 通过poetry执行的时候, 这个传入方式有问题?? -- --config=default.yaml
streamlit run run_flowagent_ui_demo.py -- --config=ui_deploy.yaml

