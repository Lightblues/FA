#!/bin/bash

cd /cephp/huabu_online/src/
uvicorn api_server.main:app --host 0.0.0.0 --port 9390 --reload --reload-dir ./api_server
