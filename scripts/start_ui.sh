#!/bin/bash

cd /mnt/huabu/src
# poetry run 
streamlit run run_flowagent_ui.py --server.address 0.0.0.0 --server.port=8502 
# 通过poetry执行的时候, 这个传入方式有问题?? -- --config=default.yaml
