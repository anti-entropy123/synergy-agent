#!/bin/bash

# 启动四个 agent 容器
docker run --rm -d --cap-add SYS_NICE --name agent-1 synergy-agent ./main -a 6 -p c
docker run --rm -d --cap-add SYS_NICE --name agent-2 synergy-agent ./main -a 12 -p c
docker run --rm -d --cap-add SYS_NICE --name agent-3 synergy-agent ./main -a 18 -p c
docker run --rm -d --cap-add SYS_NICE --name agent-4 synergy-agent ./main -a 24 -p c

echo "所有synergy agent 容器已启动。"
