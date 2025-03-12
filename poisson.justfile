export_dir := "synergy-controller/export"

sec3_run_CDF_hw:
    just run_synergy hw_500_luan_poisson > {{export_dir}}/Synergy_hw_500_luan_poisson.log
    just run_OpenFaaS hw_500_luan_poisson > {{export_dir}}/OpenFaaS_hw_500_luan_poisson.log
    just run_OpenWhisk hw_500_luan_poisson > {{export_dir}}/OpenWhisk_hw_500_luan_poisson.log
    just run_SFS hw_500_luan_poisson > {{export_dir}}/SFS_hw_500_luan_poisson.log

sec3_run_CDF_wr:
    just run_synergy wr_500_luan_poisson > {{export_dir}}/Synergy_wr_500_luan_poisson.log
    just run_OpenFaaS wr_500_luan_poisson > {{export_dir}}/OpenFaaS_wr_500_luan_poisson.log
    just run_OpenWhisk wr_500_luan_poisson > {{export_dir}}/OpenWhisk_wr_500_luan_poisson.log
    just run_SFS wr_500_luan_poisson > {{export_dir}}/SFS_wr_500_luan_poisson.log

sec3_run_SLO_hw:
    just run_synergy hw_100_luan_poisson > {{export_dir}}/Synergy_hw_100_luan_poisson.log
    just run_OpenFaaS hw_100_luan_poisson > {{export_dir}}/OpenFaaS_hw_100_luan_poisson.log
    just run_OpenWhisk hw_100_luan_poisson > {{export_dir}}/OpenWhisk_hw_100_luan_poisson.log
    just run_SFS hw_100_luan_poisson > {{export_dir}}/SFS_hw_100_luan_poisson.log

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

            p1 = subprocess.Popen(["just", "run_synergy", "hw_100_luan_poisson"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            p2 = subprocess.Popen(["grep", "Average Turn-around Time:"], stdin=p1.stdout, stdout=subprocess.PIPE, text=True)
            p1.stdout.close()
            output, _ = p2.communicate()
            if p2.returncode != 0:
                print("run_synergy_CDF failed")
                exit(1)

            print(output.strip())