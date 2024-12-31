#!/bin/bash

cd /cephp/huabu_online/src

streamlit run run_demo_frontend.py -- --config=ui_deploy.yaml
# streamlit run run_demo_frontend.py --server.port=8502  -- --config=dev.yaml
