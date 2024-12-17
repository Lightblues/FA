#!/bin/bash

cd /cephp/huabu_online/src
uvicorn backend.main:app --host 0.0.0.0 --port 8100 --reload --reload-dir ./backend
