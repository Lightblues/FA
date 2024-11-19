""" 
streamlit run run_flowagent_ui_demo.py -- --config=ui_deploy.yaml
"""
import argparse
from flowagent.ui_conv.app import main

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", type=str, default="default.yaml")
    args = args.parse_args()
    main(args.config)
