#!/bin/bash

# Script to start the server for development (https)
# Note: you will need to generate a self-signed certificate

cd app || cd ../app

uvicorn main:app --host 0.0.0.0 --port 8000 --reload --ssl-keyfile ../secrets/key.pem --ssl-certfile ../secrets/cert.pem