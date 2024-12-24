"""
Usage:
    python run_demo_backend.py --config=default.yaml
    python run_demo_backend.py --config=default.yaml --port=8101 --reload
"""

import argparse
import uvicorn
from fa_demo.backend.main import create_app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="default.yaml")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8100)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    if args.reload:
        # NOTE: in hot reload mode, must use environment variable!
        import os

        os.environ["CONFIG_NAME"] = args.config
        app_path = "fa_demo.backend.main:app"
    else:
        # in non-hot reload mode, can directly pass config
        app = create_app(args.config)
        app_path = app

    uvicorn.run(app_path, host=args.host, port=args.port, reload=args.reload, reload_dirs=["./fa_demo/backend"] if args.reload else None)


if __name__ == "__main__":
    main()
