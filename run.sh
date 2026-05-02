#!/bin/bash

#for those who don't want to use docker

export CORS=true
export MAINTENANCE=true
export MAX_MAINTENACE_DELETE_PERCENT=0.2
export MAX_MAINTENACE_REPLACE_PERCENT=0.8
uvicorn server:app --host 0.0.0.0 --port 8000