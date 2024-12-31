"""
Usage:
    python run_demo_backend.py --config=default.yaml
    python run_demo_backend.py --config=default.yaml --port=8101 --reload
"""

import os
import argparse
import urllib.parse
import uvicorn
from fa_server import create_app
from fa_core.common import Config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="default.yaml")
    parser.add_argument("--host", type=str, default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    if args.reload:
        # NOTE: in hot reload mode, must use environment variable!
        os.environ["CONFIG_NAME"] = args.config
        app_path = "fa_server.main:app"
    else:
        # in non-hot reload mode, can directly pass config
        app = create_app(args.config)
        app_path = app

    config_url = Config.from_yaml(args.config).backend_url
    host = args.host or urllib.parse.urlparse(config_url).hostname
    port = args.port or urllib.parse.urlparse(config_url).port
    uvicorn.run(app_path, host=host, port=port, reload=args.reload, reload_dirs=["./fa_demo/backend"] if args.reload else None)


if __name__ == "__main__":
    main()
