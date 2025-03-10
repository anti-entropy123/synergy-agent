silence := "0"

console_redirect := if silence == "1" {
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

start_sfs_agent:
    docker run --rm -d --cap-add SYS_NICE --name agent-11 synergy-agent ./main -a 54 -p m
    docker run --rm -d --cap-add SYS_NICE --name agent-12 synergy-agent ./main -a 60 -p m
    docker run --rm -d --cap-add SYS_NICE --name agent-13 synergy-agent ./main -a 66 -p m
    docker run --rm -d --cap-add SYS_NICE --name agent-14 synergy-agent ./main -a 72 -p m

    echo "所有synergy sfs agent 容器已启动。"

stop_sfs_agent:
    docker stop agent-11 agent-12 agent-13 agent-14

start_all: start_agent start_nocoop_agent start_sfs_agent
stop_all: stop_agent stop_nocoop_agent stop_sfs_agent

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

    for ((i=11; i<15; i++)); do \
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

    for ((i=11; i<15; i++)); do \
        sudo truncate -s 0 `docker inspect --format={{'{{.LogPath}}'}} agent-$i`; \
    done


reset_policy policy='c':
    curl -s -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.5:20251/change_policy
    curl -s -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.6:20251/change_policy
    curl -s -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.7:20251/change_policy
    curl -s -X POST -H "Content-Type: text/plain" --data 'c' http://172.17.0.8:20251/change_policy

    curl -s -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.9:20251/change_policy
    curl -s -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.10:20251/change_policy
    curl -s -X POST -H "Content-Type: text/plain" --data 'c' http://172.17.0.11:20251/change_policy
    curl -s -X POST -H "Content-Type: text/plain" --data 'c' http://172.17.0.12:20251/change_policy
    
    curl -s -X POST -H "Content-Type: text/plain" --data '{{policy}}' http://172.17.0.13:20251/change_policy
    curl -s -X POST -H "Content-Type: text/plain" --data '{{policy}}' http://172.17.0.14:20251/change_policy
    curl -s -X POST -H "Content-Type: text/plain" --data '{{policy}}' http://172.17.0.15:20251/change_policy
    curl -s -X POST -H "Content-Type: text/plain" --data '{{policy}}' http://172.17.0.16:20251/change_policy

export_agent_log:
    #!/usr/bin/bash
    cd synergy-controller/result
    for ((i=1; i<5; i++)); do \
        docker logs agent-$i > agent-$i.log; \
    done

    for ((i=6; i<10; i++)); do \
        docker logs agent-$i > agent-$i.log; \
    done

    for ((i=11; i<15; i++)); do \
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

    for ((i=11; i<15; i++)); do \
        python3 ../get_log_data.py agent-$i.log agent-$i.csv; \
    done

comp_turnaround: export_agent_log gen_csv
    cd synergy-controller/result && python3 ../merge_csv.py agent1_4.csv agent-1.csv agent-2.csv agent-3.csv agent-4.csv
    cd synergy-controller/result && python3 ../merge_csv.py agent6_9.csv agent-6.csv agent-7.csv agent-8.csv agent-9.csv
    cd synergy-controller/result && python3 ../merge_csv.py agent11_14.csv agent-11.csv agent-12.csv agent-13.csv agent-14.csv
    cd synergy-controller/result && wc -l agent1_4.csv
    cd synergy-controller/result && wc -l agent6_9.csv
    cd synergy-controller/result && wc -l agent11_14.csv

send_reqs trace='test_tiny':
    curl -X POST -H "Content-Type: text/plain" --data-binary @synergy/test_data/{{trace}} http://localhost:20251/set_reqs

run_controller trace_file="test_data/test_tiny" schedu_arg="--allowAdjust --partition" policy="c":
    just reset_policy {{policy}}
    just clear_log
    cd synergy-controller && go build scheduler.go
    sleep 1

    date '+%s.%N'
    ./synergy-controller/scheduler {{schedu_arg}} --trace ./synergy-controller/{{trace_file}} {{console_redirect}}
    date '+%s.%N'

    just export_agent_log

run_predictor:
    scp -r predictor/lstm yjn@192.168.1.183:/home/yjn/synergy-agent/predictor/
    scp -r predictor/qps_data_loader yjn@192.168.1.183:/home/yjn/synergy-agent/predictor/qps_data_loader
    # ssh yjn@192.168.1.183 'cd /home/yjn/synergy-agent/predictor/ && python3 lstm_invocation.py'
    # scp yjn@192.168.1.183:/home/yjn/synergy-agent/predictor/result.pdf predictor/lstm/lstm_output.pdf
    scp yjn@192.168.1.183:/home/yjn/synergy-agent/predictor/*.json ./predictor/results/

wait_ack_htop:
    #!/usr/bin/bash

    # read -p "检查 htop 后继续: "
    sleep 10

export_results label:
    -rm -r synergy-controller/export/result_{{label}}
    mkdir -p synergy-controller/export/result_{{label}} && cp -r synergy-controller/result synergy-controller/export/result_{{label}}

run_synergy trace='20-600': 
    @echo "run_Synergy_CDF_{{trace}} 开始执行。"
    # test_data/20-600
    # agent 1-4
    just run_controller 'test_data/{{trace}}' '--allowAdjust --partition --selectBy hash'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'Synergy_CDF_{{trace}}'
    @echo "run_Synergy_CDF_{{trace}} 执行完成。"

run_synergy_CDF:
    just run_synergy 20-600
    just run_synergy 30-300
    just run_synergy 40-200

run_OpenWhisk trace='20-600':
    @echo "run_OpenWhisk_CDF_{{trace}} 开始执行。"
    # test_data/{{trace}}
    # agent 1-4
    just run_controller 'test_data/{{trace}}' '--selectBy hash'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'OpenWhisk_CDF_{{trace}}'
    @echo "run_OpenWhisk_CDF_{{trace}} 执行完成。"

run_OpenWhisk_CDF:
    just run_OpenWhisk 20-600
    just run_OpenWhisk 30-300
    just run_OpenWhisk 40-200

run_OpenFaaS trace='20-600':
    @echo "run_OpenFaaS_CDF_{{trace}} 开始执行。"
    # test_data/20-600
    # agent 1-4
    just run_controller 'test_data/{{trace}}' '--selectBy random'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'OpenFaaS_CDF_{{trace}}'
    @echo "run_OpenFaaS_CDF_{{trace}} 执行完成。"

run_OpenFaaS_CDF:
    just run_OpenFaaS 20-600
    just run_OpenFaaS 30-300
    just run_OpenFaaS 40-200

run_SFS trace='20-600':    
    @echo "run_SFS_CDF_{{trace}} 开始执行。"
    # test_data/{{trace}}
    # agent 1-4
    just run_controller 'test_data/{{trace}}' '--selectBy hash' 'm'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'SFS_CDF_{{trace}}'
    @echo "run_SFS_CDF_{{trace}} 执行完成。"

run_SFS_CDF:
    just run_SFS 20-600
    just run_SFS 30-300
    just run_SFS 40-200

run_synergy_CDF_no_allowAdjust:
    @echo "run_Synergy_CDF_no_allowAdjust_20-600 开始执行。"
    # test_data/20-600
    # agent 1-4
    just run_controller 'test_data/20-600' '--partition --selectBy leastLoad'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'Synergy_no_allowAdjust_CDF_20-600'
    @echo "run_Synergy_CDF_no_allowAdjust_20-600 执行完成。"

    @echo "run_Synergy_CDF_no_allowAdjust_30-300 开始执行。"
    just run_controller 'test_data/30-300' '--partition --selectBy leastLoad'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'Synergy_no_allowAdjust_CDF_30-300'
    @echo "run_Synergy_CDF_no_allowAdjust_30-300 执行完成。"

    @echo "run_Synergy_CDF_no_allowAdjust_40-200 开始执行。"
    just run_controller 'test_data/40-200' '--partition --selectBy leastLoad'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'Synergy_no_allowAdjust_CDF_40-200'
    @echo "run_Synergy_CDF_no_allowAdjust_40-200 执行完成。"

run_ffff_synergy_CDF:
    @echo "run_ffff_Synergy_CDF_20-600 开始执行。"
    # test_data/20-600
    # agent 1-4
    just run_controller 'test_data/20-600' '--allowAdjust --partition --selectBy leastLoad'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'ffff_Synergy_CDF_20-600'
    @echo "run_ffff_Synergy_CDF_20-600 执行完成。"

    @echo "run_ffff_Synergy_CDF_30-300 开始执行。"
    just run_controller 'test_data/30-300' '--allowAdjust --partition --selectBy leastLoad'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'ffff_Synergy_CDF_30-300'
    @echo "run_ffff_Synergy_CDF_30-300 执行完成。"

    @echo "run_ffff_Synergy_CDF_40-200 开始执行。"
    just run_controller 'test_data/40-200' '--allowAdjust --partition --selectBy leastLoad'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'ffff_Synergy_CDF_40-200'
    @echo "run_ffff_Synergy_CDF_40-200 执行完成。"


run_Synergy_CDF_hw:
    # just run_Synergy_CDF_hw > export/Synergy_CDF_hw.log
    @echo "run_Synergy_CDF_hw 开始执行。"
    # test_data/20-600
    # agent 1-4
    just run_controller 'test_data/hw.csv' '--allowAdjust --partition --selectBy leastLoad'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'Synergy_CDF_hw'
    @echo "run_Synergy_CDF_hw 执行完成。"

run_Synergy_CDF_wr:
    # just run_Synergy_CDF_wr > export/Synergy_CDF_wr.log
    @echo "run_Synergy_CDF_wr 开始执行。"
    # test_data/20-600
    # agent 1-4
    just run_controller 'test_data/wr.csv' '--allowAdjust --partition --selectBy leastLoad'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'Synergy_CDF_wr'
    @echo "run_Synergy_CDF_wr 执行完成。"

run_OpenWhisk_CDF_hw:
    # just run_OpenWhisk_CDF_hw > export/OpenWhisk_CDF_hw.log
    @echo "run_OpenWhisk_CDF_hw 开始执行。"
    # test_data/20-600
    # agent 1-4
    just run_controller 'test_data/hw.csv' '--selectBy hash'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'OpenWhisk_CDF_hw'
    @echo "run_OpenWhisk_CDF_hw 执行完成。"

run_OpenWhisk_CDF_wr:
    # just run_OpenWhisk_CDF_wr > export/OpenWhisk_CDF_wr.log
    @echo "run_OpenWhisk_CDF_wr 开始执行。"
    # test_data/20-600
    # agent 1-4
    just run_controller 'test_data/wr.csv' '--selectBy hash'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'OpenWhisk_CDF_wr'
    @echo "run_OpenWhisk_CDF_wr 执行完成。"

run_OpenFaaS_CDF_hw:
    # just run_OpenFaaS_CDF_hw > export/OpenFaaS_CDF_hw.log
    @echo "run_OpenFaaS_CDF_hw 开始执行。"
    # test_data/20-600
    # agent 1-4
    just run_controller 'test_data/hw.csv' '--selectBy random'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'OpenFaaS_CDF_hw'
    @echo "run_OpenFaaS_CDF_hw 执行完成。"

run_OpenFaaS_CDF_wr:
    # just run_OpenFaaS_CDF_wr > export/OpenFaaS_CDF_wr.log
    @echo "run_OpenFaaS_CDF_wr 开始执行。"
    # test_data/20-600
    # agent 1-4
    just run_controller 'test_data/wr.csv' '--selectBy random'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'OpenFaaS_CDF_wr'
    @echo "run_OpenFaaS_CDF_wr 执行完成。"

run_SFS_CDF_hw:
    # just run_SFS_CDF_hw > export/SFS_CDF_hw.log
    @echo "run_SFS_CDF_hw 开始执行。"
    # test_data/20-600
    # agent 1-4
    just run_controller 'test_data/hw.csv' '--selectBy hash' 'm'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'SFS_CDF_hw'
    @echo "run_SFS_CDF_hw 执行完成。"

run_SFS_CDF_wr:
    # just run_SFS_CDF_wr > export/SFS_CDF_wr.log
    @echo "run_SFS_CDF_wr 开始执行。"
    # test_data/20-600
    # agent 1-4
    just run_controller 'test_data/wr.csv' '--selectBy hash' 'm'
    just wait_ack_htop
    just comp_turnaround
    just export_results 'SFS_CDF_wr'
    @echo "run_SFS_CDF_wr 执行完成。"

test_threshold:
    #!/usr/bin/python3
    import subprocess
    import time
    
    for not_busy in range(5, 90, 5):
        for busy in range(not_busy, 90, 5):
            print("not_busy: ", not_busy, "busy: ", busy)
            const_file = open("./synergy-controller/const.h", "w")
            const_file.write(f"#define NOT_BUSY_THRESHOLD {not_busy}\n#define BUSY_THRESHOLD {busy}\n")
            const_file.close()
            time.sleep(1)

            p1 = subprocess.Popen(["just", "run_synergy_CDF_20_600"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            p2 = subprocess.Popen(["grep", "Average Turn-around Time:"], stdin=p1.stdout, stdout=subprocess.PIPE, text=True)
            p1.stdout.close()
            output, _ = p2.communicate()
            if p2.returncode != 0:
                print("run_synergy_CDF failed")
                exit(1)

            print(output.strip())