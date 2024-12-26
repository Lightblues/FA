"""
Runs:
    streamlit run run_demo_frontend.py -- --config=ui_deploy.yaml
    streamlit run run_demo_frontend.py --server.port 8502 -- --config=dev.yaml
"""

import argparse

from fa_demo import main


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", type=str, default="default.yaml")
    args = args.parse_args()

    main(args.config)
