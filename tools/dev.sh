#!/bin/bash

export CORS=false
export MAINTENANCE=false
export LOG_LEVEL=DEBUG
uvicorn server:app --host 0.0.0.0 --port 8000 --reload