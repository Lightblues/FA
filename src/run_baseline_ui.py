""" 
> streamlit run run_baseline_ui.py
streamlit run run_baseline_ui.py --server.port=8502 -- --config=default.yaml
"""
import argparse
from baselines.ui.app import main

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", type=str, default="default.yaml")
    args = args.parse_args()
    main(args.config)
