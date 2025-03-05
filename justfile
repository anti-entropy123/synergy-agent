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


reset_policy:
    curl -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.5:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.6:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'c' http://172.17.0.7:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'c' http://172.17.0.8:20251/change_policy

    curl -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.9:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'f' http://172.17.0.10:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'c' http://172.17.0.11:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'c' http://172.17.0.12:20251/change_policy
    
    curl -X POST -H "Content-Type: text/plain" --data 'm' http://172.17.0.13:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'm' http://172.17.0.14:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'm' http://172.17.0.15:20251/change_policy
    curl -X POST -H "Content-Type: text/plain" --data 'm' http://172.17.0.16:20251/change_policy

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
    curl -X POST -H "Content-Type: text/plain" --data-binary @synergy-controller/{{trace}} http://localhost:20251/set_reqs

run_controller trace_file="test_tiny":
    #!/usr/bin/bash
    
    just reset_policy
    just clear_log
    cd synergy-controller && go build scheduler.go
    sleep 3

    export trace_file={{trace_file}}

    date '+%s.%N'
    ./scheduler --allowAdjust --trace $trace_file {{console_redirect}}
    date '+%s.%N'
    ./scheduler --trace $trace_file {{console_redirect}}
    date '+%s.%N'
    just export_agent_log

run_predictor:
    scp -r predictor/lstm yjn@192.168.1.183:/home/yjn/synergy-agent/predictor/
    scp -r predictor/qps_data_loader yjn@192.168.1.183:/home/yjn/synergy-agent/predictor/qps_data_loader
    # ssh yjn@192.168.1.183 'cd /home/yjn/synergy-agent/predictor/ && python3 lstm_invocation.py'
    # scp yjn@192.168.1.183:/home/yjn/synergy-agent/predictor/result.pdf predictor/lstm/lstm_output.pdf
    scp yjn@192.168.1.183:/home/yjn/synergy-agent/predictor/*.json ./predictor/results/

run_synergy_CDF:
    echo "run_Synergy_CDF_20-600 开始执行。"
    # run_Synergy_CDF_20-600:
    just reset_policy
    just clear_log
    ./synergy-controller/scheduler --allowAdjust --partition --selectBy leastLoad --trace synergy-controller/test_data/20-600
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_Synergy_CDF_20-600
    mkdir -p export && mkdir -p synergy-controller/export/result_Synergy_CDF_20-600 && cp -r synergy-controller/result  synergy-controller/export/result_Synergy_CDF_20-600
    echo "run_Synergy_CDF_20-600 执行完成。"

    echo "------------------------------\n"

    echo "run_Synergy_CDF_30-300 开始执行。"
    # run_Synergy_CDF_30-300:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --allowAdjust --partition --selectBy leastLoad --trace synergy-controller/test_data/30-300
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_Synergy_CDF_30-300
    mkdir -p export && mkdir -p synergy-controller/export/result_Synergy_CDF_30-300 && cp -r synergy-controller/result  synergy-controller/export/result_Synergy_CDF_30-300
    echo "run_Synergy_CDF_30-300 执行完成。"
    
    echo "run_Synergy_CDF_40-200 开始执行。"
    # run_Synergy_CDF_40-200:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --allowAdjust --partition --selectBy leastLoad --trace synergy-controller/test_data/40-200
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_Synergy_CDF_40-200
    mkdir -p export && mkdir -p synergy-controller/export/result_Synergy_CDF_40-200 && cp -r synergy-controller/result  synergy-controller/export/result_Synergy_CDF_40-200
    echo "run_Synergy_CDF_40-200 执行完成。"

run_OpenWhisk_CDF:
    echo "run_OpenWhisk_CDF_20-600 开始执行。"
    # run_OpenWhisk_CDF_20-600:
    # 分区改为CFS
    just reset_policy
    just clear_log
    ./synergy-controller/scheduler --selectBy hash --trace synergy-controller/test_data/20-600
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_OpenWhisk_CDF_20-600
    mkdir -p export && mkdir -p synergy-controller/export/result_OpenWhisk_CDF_20-600 && cp -r synergy-controller/result  synergy-controller/export/result_OpenWhisk_CDF_20-600
    echo "run_OpenWhisk_CDF_20-600 执行完成。"

    echo "------------------------------\n"

    echo "run_OpenWhisk_CDF_30-300 开始执行。"
    # run_OpenWhisk_CDF_30-300:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --selectBy hash --trace synergy-controller/test_data/30-300
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_OpenWhisk_CDF_30-300
    mkdir -p export && mkdir -p synergy-controller/export/result_OpenWhisk_CDF_30-300 && cp -r synergy-controller/result  synergy-controller/export/result_OpenWhisk_CDF_30-300
    echo "run_OpenWhisk_CDF_30-300 执行完成。"
    
    echo "run_OpenWhisk_CDF_40-200 开始执行。"
    # run_OpenWhisk_CDF_40-200:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --selectBy hash --trace synergy-controller/test_data/40-200
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_OpenWhisk_CDF_40-200
    mkdir -p export && mkdir -p synergy-controller/export/result_OpenWhisk_CDF_40-200 && cp -r synergy-controller/result  synergy-controller/export/result_OpenWhisk_CDF_40-200
    echo "run_OpenWhisk_CDF_40-200 执行完成。"

run_OpenFaaS_CDF1:
    echo "run_OpenFaaS_CDF_20-600 开始执行。"
    # run_OpenFaaS_CDF_20-600:
    # 分区改为CFS
    just reset_policy
    just clear_log
    ./synergy-controller/scheduler --selectBy random --trace synergy-controller/test_data/20-600
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_OpenFaaS_CDF_20-600
    mkdir -p export && mkdir -p synergy-controller/export/result_OpenFaaS_CDF_20-600 && cp -r synergy-controller/result  synergy-controller/export/result_OpenFaaS_CDF_20-600
    echo "run_OpenFaaS_CDF_20-600 执行完成。"

run_OpenFaaS_CDF2:
    echo "run_OpenFaaS_CDF_30-300 开始执行。"
    # run_OpenFaaS_CDF_30-300:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --selectBy random --trace synergy-controller/test_data/30-300
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_OpenFaaS_CDF_30-300
    mkdir -p export && mkdir -p synergy-controller/export/result_OpenFaaS_CDF_30-300 && cp -r synergy-controller/result  synergy-controller/export/result_OpenFaaS_CDF_30-300
    echo "run_OpenFaaS_CDF_30-300 执行完成。"

run_OpenFaaS_CDF3:   
    echo "run_OpenFaaS_CDF_40-200 开始执行。"
    # run_OpenFaaS_CDF_40-200:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --selectBy random --trace synergy-controller/test_data/40-200
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_OpenFaaS_CDF_40-200
    mkdir -p export && mkdir -p synergy-controller/export/result_OpenFaaS_CDF_40-200 && cp -r synergy-controller/result  synergy-controller/export/result_OpenFaaS_CDF_40-200
    echo "run_OpenFaaS_CDF_40-200 执行完成。"

run_SFS_CDF:
    echo "run_SFS_CDF_20-600 开始执行。"
    # run_SFS_CDF_20-600:
    # 分区改为CFS
    just reset_policy
    just clear_log
    ./synergy-controller/scheduler --selectBy hash --trace synergy-controller/test_data/20-600
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_SFS_CDF_20-600
    mkdir -p export && mkdir -p synergy-controller/export/result_SFS_CDF_20-600 && cp -r synergy-controller/result  synergy-controller/export/result_SFS_CDF_20-600
    echo "run_SFS_CDF_20-600 执行完成。"

    echo "------------------------------\n"

    echo "run_SFS_CDF_30-300 开始执行。"
    # run_SFS_CDF_30-300:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --selectBy hash --trace synergy-controller/test_data/30-300
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_SFS_CDF_30-300
    mkdir -p export && mkdir -p synergy-controller/export/result_SFS_CDF_30-300 && cp -r synergy-controller/result  synergy-controller/export/result_SFS_CDF_30-300
    echo "run_SFS_CDF_30-300 执行完成。"
    
    echo "run_SFS_CDF_40-200 开始执行。"
    # run_SFS_CDF_40-200:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --selectBy hash --trace synergy-controller/test_data/40-200
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_SFS_CDF_40-200
    mkdir -p export && mkdir -p synergy-controller/export/result_SFS_CDF_40-200 && cp -r synergy-controller/result  synergy-controller/export/result_SFS_CDF_40-200
    echo "run_SFS_CDF_40-200 执行完成。"

run_synergy_CDF_no_allowAdjust:
    echo "run_Synergy_CDF_no_allowAdjust_20-600 开始执行。"
    # run_Synergy_CDF_no_allowAdjust_20-600:
    just reset_policy
    just clear_log
    ./synergy-controller/scheduler --partition --selectBy leastLoad --trace synergy-controller/test_data/20-600
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_Synergy_CDF_no_allowAdjust_20-600
    mkdir -p export && mkdir -p synergy-controller/export/result_Synergy_CDF_no_allowAdjust_20-600 && cp -r synergy-controller/result  synergy-controller/export/result_Synergy_CDF_no_allowAdjust_20-600
    echo "run_Synergy_CDF_no_allowAdjust_20-600 执行完成。"

    echo "------------------------------\n"

    echo "run_Synergy_CDF_no_allowAdjust_30-300 开始执行。"
    # run_Synergy_CDF_no_allowAdjust_30-300:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --partition --selectBy leastLoad --trace synergy-controller/test_data/30-300
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_Synergy_no_allowAdjust_CDF_30-300
    mkdir -p export && mkdir -p synergy-controller/export/result_Synergy_CDF_no_allowAdjust_30-300 && cp -r synergy-controller/result  synergy-controller/export/result_Synergy_CDF_no_allowAdjust_30-300
    echo "run_Synergy_CDF_no_allowAdjust_30-300 执行完成。"
    
    echo "run_Synergy_CDF_no_allowAdjust_40-200 开始执行。"
    # run_Synergy_CDF_no_allowAdjust_40-200:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --partition --selectBy leastLoad --trace synergy-controller/test_data/40-200
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_Synergy_CDF_no_allowAdjust_40-200
    mkdir -p export && mkdir -p synergy-controller/export/result_Synergy_CDF_no_allowAdjust_40-200 && cp -r synergy-controller/result  synergy-controller/export/result_Synergy_CDF_no_allowAdjust_40-200
    echo "run_Synergy_CDF_no_allowAdjust_40-200 执行完成。"

run_ffff_synergy_CDF:
    echo "run_ffff_Synergy_CDF_20-600 开始执行。"
    # run_ffff_Synergy_CDF_20-600:
    just reset_policy
    just clear_log
    ./synergy-controller/scheduler --allowAdjust --partition --selectBy leastLoad --trace synergy-controller/test_data/20-600
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_ffff_Synergy_CDF_20-600
    mkdir -p export && mkdir -p synergy-controller/export/result_ffff_Synergy_CDF_20-600 && cp -r synergy-controller/result  synergy-controller/export/result_ffff_Synergy_CDF_20-600
    echo "run_ffff_Synergy_CDF_20-600 执行完成。"

    echo "------------------------------\n"

    echo "run_ffff_Synergy_CDF_30-300 开始执行。"
    # run_ffff_Synergy_CDF_30-300:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --allowAdjust --partition --selectBy leastLoad --trace synergy-controller/test_data/30-300
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_ffff_Synergy_CDF_30-300
    mkdir -p export && mkdir -p synergy-controller/export/result_ffff_Synergy_CDF_30-300 && cp -r synergy-controller/result  synergy-controller/export/result_ffff_Synergy_CDF_30-300
    echo "run_ffff_Synergy_CDF_30-300 执行完成。"
    
    echo "run_ffff_Synergy_CDF_40-200 开始执行。"
    # run_ffff_Synergy_CDF_40-200:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --allowAdjust --partition --selectBy leastLoad --trace synergy-controller/test_data/40-200
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export/result_ffff_Synergy_CDF_40-200
    mkdir -p export && mkdir -p synergy-controller/export/result_ffff_Synergy_CDF_40-200 && cp -r synergy-controller/result  synergy-controller/export/result_ffff_Synergy_CDF_40-200
    echo "run_ffff_Synergy_CDF_40-200 执行完成。"

run_synergy_CDF_hw:
    echo "run_Synergy_CDF_hw 开始执行。"
    # run_Synergy_CDF_hw:
    just reset_policy
    just clear_log
    ./synergy-controller/scheduler --allowAdjust --partition --selectBy leastLoad --trace synergy-controller/test_data/hw.csv
    sleep 2
    just comp_turnaround
    sleep 2
    rm -r synergy-controller/export2/result_Synergy_CDF_hw
    mkdir -p export2 && mkdir -p synergy-controller/export2/result_Synergy_CDF_hw && cp -r synergy-controller/result  synergy-controller/export2/result_Synergy_CDF_hw
    echo "run_Synergy_CDF_hw 执行完成。"

run_synergy_CDF_wr:
    echo "run_Synergy_CDF_wr 开始执行。"
    # run_Synergy_CDF_wr:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --allowAdjust --partition --selectBy leastLoad --trace synergy-controller/test_data/wr.csv
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export2/result_Synergy_CDF_wr
    mkdir -p export2 && mkdir -p synergy-controller/export2/result_Synergy_CDF_wr && cp -r synergy-controller/result  synergy-controller/export2/result_Synergy_CDF_wr
    echo "run_Synergy_CDF_wr 执行完成。"

run_OpenWhisk_CDF_hw:
    echo "run_OpenWhisk_CDF_hw 开始执行。"
    # run_OpenWhisk_CDF_hw:
    # 分区改为CFS
    just reset_policy
    just clear_log
    ./synergy-controller/scheduler --selectBy hash --trace synergy-controller/test_data/hw.csv
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export2/result_OpenWhisk_CDF_hw
    mkdir -p export2 && mkdir -p synergy-controller/export2/result_OpenWhisk_CDF_hw && cp -r synergy-controller/result  synergy-controller/export2/result_OpenWhisk_CDF_hw
    echo "run_OpenWhisk_CDF_hw 执行完成。"

run_OpenWhisk_CDF_wr:
    echo "run_OpenWhisk_CDF_wr 开始执行。"
    # run_OpenWhisk_CDF_wr:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --selectBy hash --trace synergy-controller/test_data/wr.csv
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export2/result_OpenWhisk_CDF_wr
    mkdir -p export2 && mkdir -p synergy-controller/export2/result_OpenWhisk_CDF_wr && cp -r synergy-controller/result  synergy-controller/export2/result_OpenWhisk_CDF_wr
    echo "run_OpenWhisk_CDF_wr 执行完成。"

run_OpenFaaS_CDF_hw:
    echo "run_OpenFaaS_CDF_hw 开始执行。"
    # run_OpenFaaS_CDF_hw:
    # 分区改为CFS
    just reset_policy
    just clear_log
    ./synergy-controller/scheduler --selectBy random --trace synergy-controller/test_data/hw.csv
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export2/result_OpenFaaS_CDF_hw
    mkdir -p export2 && mkdir -p synergy-controller/export2/result_OpenFaaS_CDF_hw && cp -r synergy-controller/result  synergy-controller/export2/result_OpenFaaS_CDF_hw
    echo "run_OpenFaaS_CDF_hw 执行完成。"

run_OpenFaaS_CDF_wr:
    echo "run_OpenFaaS_CDF_wr 开始执行。"
    # run_OpenFaaS_CDF_wr:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --selectBy random --trace synergy-controller/test_data/wr.csv
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export2/result_OpenFaaS_CDF_wr
    mkdir -p export2 && mkdir -p synergy-controller/export2/result_OpenFaaS_CDF_wr && cp -r synergy-controller/result  synergy-controller/export2/result_OpenFaaS_CDF_wr
    echo "run_OpenFaaS_CDF_wr 执行完成。"

run_SFS_CDF_hw:
    echo "run_SFS_CDF_hw 开始执行。"
    # run_SFS_CDF_hw:
    # 分区改为CFS
    just reset_policy
    just clear_log
    ./synergy-controller/scheduler --selectBy hash --trace synergy-controller/test_data/hw.csv
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export2/result_SFS_CDF_hw
    mkdir -p export2 && mkdir -p synergy-controller/export2/result_SFS_CDF_hw && cp -r synergy-controller/result  synergy-controller/export2/result_SFS_CDF_hw
    echo "run_SFS_CDF_hw 执行完成。"

run_SFS_CDF_wr:
    echo "run_SFS_CDF_wr 开始执行。"
    # run_SFS_CDF_wr:
    just reset_policy
    just clear_log
    sleep 2
    ./synergy-controller/scheduler --selectBy hash --trace synergy-controller/test_data/wr.csv
    sleep 2
    just comp_turnaround
    rm -r synergy-controller/export2/result_SFS_CDF_wr
    mkdir -p export2 && mkdir -p synergy-controller/export2/result_SFS_CDF_wr && cp -r synergy-controller/result  synergy-controller/export2/result_SFS_CDF_wr
    echo "run_SFS_CDF_wr0 执行完成。"