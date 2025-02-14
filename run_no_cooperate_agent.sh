#!/bin/bash

# 启动四个 agent 容器
docker run --rm -d --cap-add SYS_NICE --name agent-6 synergy-agent ./main -a 30 -p f
docker run --rm -d --cap-add SYS_NICE --name agent-7 synergy-agent ./main -a 36 -p f
docker run --rm -d --cap-add SYS_NICE --name agent-8 synergy-agent ./main -a 42 -p c
docker run --rm -d --cap-add SYS_NICE --name agent-9 synergy-agent ./main -a 48 -p c

echo "所有no_cooperate agent 容器已启动。"