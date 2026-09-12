#!/bin/bash

docker build -t aceandgaming/swarmtunesserver:v2 .
docker run --rm -p 8000:8000 aceandgaming/swarmtunesserver:v2