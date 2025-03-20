import os
import numpy as np
import json
import jsonlines
from collections import defaultdict

dict = defaultdict(list)
folders = ["/raid/xuyifan/Android-Lab-main/logs/android_world/v26_android_world_250312_text_1history_launch_filter300_aw_train_sample-0317-3e-1","/raid/xuyifan/Android-Lab-main/logs/android_world/v26_android_world_250312_text_1history_launch_filter300_aw_train_sample-0317-3e-2","/raid/xuyifan/Android-Lab-main/logs/android_world/v26_android_world_250312_text_1history_launch_filter300_aw_train_sample-0317-3e-3","/raid/xuyifan/Android-Lab-main/logs/android_world/v26_android_world_250312_text_1history_launch_filter300_aw_train_sample-0317-3e-4","/raid/xuyifan/Android-Lab-main/logs/android_world/v26_android_world_250312_text_1history_launch_filter300_aw_train_sample-0317-3e-5","/raid/xuyifan/Android-Lab-main/logs/android_world/v26_android_world_250312_text_1history_launch_filter300_aw_train_sample-0317-3e-6","/raid/xuyifan/Android-Lab-main/logs/android_world/v26_android_world_250312_text_1history_launch_filter300_aw_train_sample-0317-3e-7","/raid/xuyifan/Android-Lab-main/logs/android_world/v26_android_world_250312_text_1history_launch_filter300_aw_train_sample-0317-3e-8"]
#folder = "/raid/xuyifan/Android-Lab-main/logs/android_world/v26_android_world_250307_1history-3e-fix-sample-ir"
for folder in folders:
    for file in os.listdir(folder):
        task_name = file.split("_")[0]
        if not os.path.exists(os.path.join(folder, file, "results.jsonl")):
            print(f"Task {file} not found")
            continue
        with jsonlines.open(os.path.join(folder, file, "results.jsonl"), "r") as f:
            for line in f:
                if isinstance(line["is_successful"], float):
                    if np.isnan(line["is_successful"]):
                        continue
                    dict[task_name].append(line["is_successful"])

score_range = []
print(len(dict))
for task_name, results in dict.items():  
    print(task_name, sum(results) / len(results))
    score_range.append(sum(results) / len(results))

# 输出score_range在0-1中每0.1的个数，比如第一组包含0-0.1，第二组包含0.1-0.2，以此类推,并且单独输出为0的数量
ranges = np.arange(0, 1.1, 0.1)
hist, _ = np.histogram(score_range, bins=ranges)
for i in range(len(hist)):
    print(f"分数区间 {ranges[i]:.1f}-{ranges[i+1]:.1f}: {hist[i]}个任务")
print(f"分数为0的数量: {score_range.count(0)}")

# 把每个任务对应的准确率存储到excel
import pandas as pd

# 创建一个字典来存储每个任务的准确率
task_accuracy = {}

# 遍历每个任务
for task_name, results in dict.items():
    # 计算准确率
    accuracy = sum(results) / len(results)
    # 存储准确率
    task_accuracy[task_name] = accuracy 

# 把task_accuracy存储到excel
df = pd.DataFrame(task_accuracy, index=["准确率"])


# 转置存储，且按字典顺序排序task name
df = df.T
df = df.sort_index()
df.to_excel("task_accuracy.xlsx")



