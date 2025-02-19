slice := "1"

console_redirect := if slice == "1" {
    "&>/dev/null"
} else {
    ""
}

start_agent:
    #!/usr/bin/bash
    for i in {1..4}; do
        docker run --rm -d --cap-add SYS_NICE --name agent-$i synergy-agent ./main -a $((i * 6)) -p c
    done

    echo "所有synergy agent 容器已启动。"

stop_agent:
    docker stop agent-1 agent-2 agent-3 agent-4

start_nocoop_agent:
    docker run --rm -d --cap-add SYS_NICE --name agent-6 synergy-agent ./main -a 30 -p f
    docker run --rm -d --cap-add SYS_NICE --name agent-7 synergy-agent ./main -a 36 -p f
    docker run --rm -d --cap-add SYS_NICE --name agent-8 synergy-agent ./main -a 42 -p c
    docker run --rm -d --cap-add SYS_NICE --name agent-9 synergy-agent ./main -a 48 -p c

    echo "所有synergy nocoop agent 容器已启动。"

stop_nocoop_agent:
    docker stop agent-6 agent-7 agent-8 agent-9

stop_all: stop_agent stop_nocoop_agent

build_agent_image:
    cd SFS-standalone && go build .
    docker build --network host --build-arg HTTP_PROXY=http://127.0.0.1:8888 --build-arg HTTPS_PROXY=http://127.0.0.1:8888 -t synergy-agent .

loopup_ip:
    #!/usr/bin/bash
    for ((i=1; i<5; i++)); do \
        echo "agent-$i: `docker inspect agent-$i | grep -m 1 '"IPAddress"'`"; \
    done

    for ((i=6; i<10; i++)); do \
        echo "agent-$i: `docker inspect agent-$i | grep -m 1 '"IPAddress"'`"; \
    done

clear_log:
    #!/usr/bin/bash
    for ((i=1; i<5; i++)); do \
        sudo truncate -s 0 `docker inspect --format={{'{{.LogPath}}'}} agent-$i`; \
    done

    for ((i=6; i<10; i++)); do \
        sudo truncate -s 0 `docker inspect --format={{'{{.LogPath}}'}} agent-$i`; \
    done

reset_policy:
    curl -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.5:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.6:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'c' http://172.17.0.7:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'c' http://172.17.0.8:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.9:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.10:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'c' http://172.17.0.11:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'c' http://172.17.0.12:20251/change_policy

export_agent_log:
    #!/usr/bin/bash
    cd synergy-controller/result
    for ((i=1; i<5; i++)); do \
        docker logs agent-$i > agent-$i.log; \
    done

    for ((i=6; i<10; i++)); do \
        docker logs agent-$i > agent-$i.log; \
    done

gen_csv:
    #!/usr/bin/bash
    cd synergy-controller/result
    for ((i=1; i<5; i++)); do \
        python3 ../get_log_data.py agent-$i.log agent-$i.csv; \
    done

    for ((i=6; i<10; i++)); do \
        python3 ../get_log_data.py agent-$i.log agent-$i.csv; \
    done

comp_turnaround: gen_csv
    cd synergy-controller/result && python3 ../merge_csv.py agent1_4.csv agent-1.csv agent-2.csv agent-3.csv agent-4.csv
    cd synergy-controller/result && python3 ../merge_csv.py agent6_9.csv agent-6.csv agent-7.csv agent-8.csv agent-9.csv

send_reqs:
    curl -X POST -H "Content-Type: text/plain" --data-binary @synergy-controller/test_tiny http://localhost:20251/set_reqs

run_controller:
    #!/usr/bin/bash
    
    just reset_policy
    just clear_log
    cd synergy-controller && go build scheduler.go
    sleep 3

    date '+%s.%N'
    ./scheduler --allowAdjust --trace test_med {{console_redirect}}
    date '+%s.%N'
    ./scheduler --trace test_med {{console_redirect}}
    date '+%s.%N'
    just export_agent_log