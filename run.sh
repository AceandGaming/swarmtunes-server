#!/bin/bash

#for those who don't want to use docker

export CORS=true
export MAINTENANCE=true
uvicorn server:app --host 0.0.0.0 --port 8000