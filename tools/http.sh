#!/bin/bash

# Script to start the server for development (http)

cd app || cd ../app

uvicorn main:app --host 0.0.0.0 --port 8000 --reload