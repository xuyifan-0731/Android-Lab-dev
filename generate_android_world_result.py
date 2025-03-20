import pandas as pd
import os

base_folder = "/raid/xuyifan/Android-Lab-main/logs/android_world"
files = os.listdir(base_folder)

# 存储所有模型的结果
all_results = []

for file in files:
    model_name = file
    result_path = os.path.join(base_folder, file, "results.xlsx")

    if not os.path.exists(result_path):
        continue

    print(f"Processing: {model_name}")
    result_df = pd.read_excel(result_path)

    # 计算指标
    sum_num_complete_trials = result_df["num_complete_trials"].sum()
    real_success_rate = result_df["mean_success_rate"].sum() / 116
    mean_complete_success_rate = result_df["mean_success_rate"].mean()

    # 记录结果
    all_results.append([
        model_name,
        sum_num_complete_trials,
        real_success_rate,
        mean_complete_success_rate
    ])

# 转换为 DataFrame 并排序
summary_df = pd.DataFrame(
    all_results,
    columns=["Model", "Sum_num_complete_trials", "Real_success_rate", "Mean_complete_success_rate"]
)
summary_df = summary_df.sort_values(by="Real_success_rate", ascending=False)

# 打印结果
print(summary_df.to_string(index=False))

# 如果需要保存结果
output_path = os.path.join(base_folder, "model_performance_summary.xlsx")
summary_df.to_excel(output_path, index=False)
print(f"Results saved to {output_path}")
