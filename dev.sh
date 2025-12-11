#!/bin/bash
cd /home/swarmtunes/server || exit 1

export DATA_PATH=dev
exec /usr/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --reload
