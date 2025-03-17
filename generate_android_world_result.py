import pandas as pd
import jsonlines
import os

base_folder = "/raid/xuyifan/Android-Lab-main/logs/android_world"
files = os.listdir(base_folder)
for file in files:
    model_name = file
    if "sample" in model_name:
        continue
    if not os.path.exists(os.path.join(base_folder, file, "results.xlsx")):
        continue
    print(file)
    result_df = pd.read_excel(os.path.join(base_folder, file, "results.xlsx"))
    # 计算 num_complete_trials 的和与平均值
    sum_num_complete_trials = result_df["num_complete_trials"].sum()
    real_success_rate = result_df["mean_success_rate"].sum()/116
    mean_complete_success_rate = result_df["mean_success_rate"].mean()

    # 创建结果 DataFrame
    result_df = pd.DataFrame({
        "Metric": ["Sum_num_complete_trials", "Real_success_rate", "Mean_complete_success_rate"],
        "Value": [sum_num_complete_trials, real_success_rate, mean_complete_success_rate]
    })

    # 输出结果
    print(result_df)



    