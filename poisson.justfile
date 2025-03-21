export_dir := "synergy-controller/export"

wait_ack_htop:
    #!/usr/bin/bash

    read -p "检查 htop 后继续: "
    # sleep 5

sec_run_CDF trace:
    just run_synergy {{trace}}_500_luan_poisson | tee {{export_dir}}/Synergy_{{trace}}_500_luan_poisson.log
    just run_OpenFaaS {{trace}}_500_luan_poisson | tee {{export_dir}}/OpenFaaS_{{trace}}_500_luan_poisson.log
    just run_OpenWhisk {{trace}}_500_luan_poisson | tee {{export_dir}}/OpenWhisk_{{trace}}_500_luan_poisson.log
    just run_SFS {{trace}}_500_luan_poisson | tee {{export_dir}}/SFS_{{trace}}_500_luan_poisson.log

sec3_run_CDF_hw:
    just -f poisson.justfile sec3_run_CDF hw

sec3_run_CDF_wr:
    just -f poisson.justfile sec3_run_CDF wr

sec3_run_SLO trace:
    # 还可以试试 c=1 的配置. 
    just run_synergy {{trace}}_100_slo | tee {{export_dir}}/Synergy_{{trace}}_100_slo.log
    just run_OpenFaaS {{trace}}_100_slo | tee {{export_dir}}/OpenFaaS_{{trace}}_100_slo.log
    just run_OpenWhisk {{trace}}_100_slo | tee {{export_dir}}/OpenWhisk_{{trace}}_100_slo.log
    just run_SFS {{trace}}_100_slo | tee {{export_dir}}/SFS_{{trace}}_100_slo.log

    just comp_slo_violate {{trace}} >> {{export_dir}}/sec3_slo_box_{{trace}}.log

sec3_run_SLO_hw:
    just -f poisson.justfile sec3_run_SLO hw

sec3_run_SLO_wr:
    just -f poisson.justfile sec3_run_SLO wr

sec3_run_SLO_box:
    # echo '' > {{export_dir}}/sec3_slo_box_hw.log
    # for i in $(seq 1 10); do \
        # just -f poisson.justfile sec3_run_SLO_hw ;\
    # done

    echo '' > {{export_dir}}/sec3_slo_box_wr.log
    for i in $(seq 1 10); do \
        just -f poisson.justfile sec3_run_SLO_wr ;\
    done

sec4_run_forceadj trace:
    just run_synergy_force '{{trace}}_500_burst' | tee {{export_dir}}/Synergy_force_{{trace}}_500_burst.log | grep 'Average Turn-around Time:'
    just run_synergy '{{trace}}_500_burst' | tee {{export_dir}}/Synergy_{{trace}}_500_burst.log | grep 'Average Turn-around Time:'
    just run_OpenFaaS '{{trace}}_500_burst' | tee {{export_dir}}/OpenFaaS_{{trace}}_500_burst.log | grep 'Average Turn-around Time:'
    just run_OpenWhisk '{{trace}}_500_burst' | tee {{export_dir}}/OpenWhisk_{{trace}}_500_burst.log | grep 'Average Turn-around Time:'
    just run_SFS '{{trace}}_500_burst' | tee {{export_dir}}/SFS_{{trace}}_500_burst.log | grep 'Average Turn-around Time:'
    
    # just -f poisson.justfile wait_ack_htop
    # just comp_turnaround | grep 'Average Turn-around Time:'
    # just export_results 'Synergy_CDF_{{trace}}_500_burst'
    # @echo "run_Synergy_CDF_{{trace}}_500_burst 执行完成。"

sec4_run_forceadj_hw:
    just -f 'poisson.justfile' sec4_run_forceadj hw

sec4_run_forceadj_wr:
    just -f 'poisson.justfile' sec4_run_forceadj wr
