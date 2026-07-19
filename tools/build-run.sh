#!/bin/bash

docker build -t aceandgaming/swarmtunesserver:v2 .
docker run --rm aceandgaming/swarmtunesserver:v2