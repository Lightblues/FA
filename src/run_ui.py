""" 
> streamlit run run_ui.py
"""
import argparse
from ui.ui_main import main

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", type=str, default="default.yaml")
    args = args.parse_args()
    main(args.config)
