"""
Usage::

    # Method 1: Run with uvicorn directly
    cd src
    CONFIG_NAME=default.yaml uvicorn fa_server.main:app --host 0.0.0.0 --port 8100 --reload --reload-dir ./fa_demo/backend

    # Method 2: Run with python script
    cd src
    python run_demo_backend.py --config=default.yaml
    python run_demo_backend.py --config=default.yaml --port=8100 --reload
"""

from fa_server.fastapi_app import init_app, setup_router

# For direct usage with uvicorn (environment variable based)
app = init_app()  # NOTE: will use os.environ["CONFIG_NAME"]
setup_router(app)
