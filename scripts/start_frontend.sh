#!/bin/bash

cd /cephp/huabu_online/src

streamlit run run_flowagent_ui2.py -- --config=ui_deploy.yaml
# streamlit run run_flowagent_ui.py --server.port=8502  -- --config=default.yaml --page_default_index=1
