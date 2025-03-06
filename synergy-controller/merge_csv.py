import sys
import pandas as pd
import os

def merge_and_calculate_avg(csv_files, output_file):
    all_data = []
    
    # 读取所有 CSV 文件并合并
    for file in csv_files:
        with open(file, "r") as f:
            if not f.read():
                return

        df = pd.read_csv(file)
        all_data.append(df)
    
    merged_df = pd.concat(all_data, ignore_index=True).sort_values(by="turn-round time")

    # 计算平均周转时间
    avg_turnaround_time = merged_df["turn-round time"].mean()
    
    # 保存合并后的数据
    merged_df.to_csv(output_file, index=False)
    
    result = f"Merged CSV saved to: {output_file}\nAverage Turn-around Time: {avg_turnaround_time:.2f}"

    with open(f'{output_file}.txt', 'w') as f:
        f.write(result)

    print(result)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python merge_csv.py <output_file.csv> <input1.csv> <input2.csv> ...")
        sys.exit(1)
    
    output_filename = sys.argv[1]
    input_files = sys.argv[2:]
    
    merge_and_calculate_avg(input_files, output_filename)
