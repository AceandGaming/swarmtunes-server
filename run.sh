#!/bin/bash
cd /home/bil/swarmtunesServer || exit 1
#source venv/bin/activate
exec /usr/bin/uvicorn server:app --host 0.0.0.0 --port 8000
