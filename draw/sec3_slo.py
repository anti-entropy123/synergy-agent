import pandas as pd

slo_ratio = 1.5

trace = "hw_100"
hw_sg_trace = pd.read_csv(f'./synergy-controller/export/result_Synergy_CDF_{trace}_luan_poisson/result/agent1_8.csv')
hw_sg_stage1 = hw_sg_trace['t1-t0'].mean()
hw_sg_stage2 = 7.5
hw_sg_stage3 = hw_sg_trace['t2-t1'].mean()
hw_sg_stage4 = hw_sg_trace['cpu time'].mean()

print("synergy SLO 违约率:", 100 * sum([1 for item in hw_sg_trace.iloc() if item['cpu time'] * slo_ratio < item['turn-round time']]))

hw_of_trace = pd.read_csv(f'./synergy-controller/export/result_OpenFaaS_CDF_{trace}_luan_poisson/result/agent21_28.csv')
hw_of_stage1 = hw_of_trace['t1-t0'].mean()
hw_of_stage2 = 0
hw_of_stage3 = hw_of_trace['t2-t1'].mean()
hw_of_stage4 = hw_of_trace['cpu time'].mean()

print("openfaas SLO 违约率:", 100 * sum([1 for item in hw_of_trace.iloc() if item['cpu time'] * slo_ratio < item['turn-round time']]))

hw_ow_trace = pd.read_csv(f'./synergy-controller/export/result_OpenWhisk_CDF_{trace}_luan_poisson/result/agent21_28.csv')
hw_ow_stage1 = hw_ow_trace['t1-t0'].mean()
hw_ow_stage2 = 0
hw_ow_stage3 = hw_ow_trace['t2-t1'].mean()
hw_ow_stage4 = hw_ow_trace['cpu time'].mean()

print("openwhisk SLO 违约率:", 100 * sum([1 for item in hw_ow_trace.iloc() if item['cpu time'] * slo_ratio < item['turn-round time']]))

hw_sfs_trace = pd.read_csv(f'./synergy-controller/export/result_SFS_CDF_{trace}_luan_poisson/result/agent21_28.csv')
hw_sfs_stage1 = hw_sfs_trace['t1-t0'].mean()
hw_sfs_stage2 = 0
hw_sfs_stage3 = hw_sfs_trace['t2-t1'].mean()
hw_sfs_stage4 = hw_sfs_trace['cpu time'].mean()

print("sfs SLO 违约率:", 100 * sum([1 for item in hw_sfs_trace.iloc() if item['cpu time'] * slo_ratio < item['turn-round time']]))
