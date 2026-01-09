#!/bin/bash
cd /home/swarmtunes/server || exit 1

#replace "swarmtunes" the user the manages the server
sudo -u swarmtunes DATA_PATH=data /usr/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --reload