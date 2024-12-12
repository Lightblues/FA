""" 
Runs: 
    streamlit run run_flowagent_ui2.py -- --config=ui_deploy.yaml
    streamlit run run_flowagent_ui2.py --server.port 8502 -- --config=ui_dev.yaml
"""
import argparse
from frontend.app import main

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", type=str, default="ui_deploy.yaml")
    args.add_argument("--page_default_index", type=int, default=0)
    args = args.parse_args()
    main(args.config, args.page_default_index)
