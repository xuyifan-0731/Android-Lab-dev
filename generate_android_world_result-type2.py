import pandas as pd
import os
import jsonlines
import numpy as np
from collections import defaultdict

base_folder = "/raid/xuyifan/Android-Lab-main/logs/android_world"
files = os.listdir(base_folder)

# 存储所有模型的结果
all_results = []
all_task_df = []
for file in files:
    model_name = file
    if not os.path.isdir(os.path.join(base_folder, file)):
        continue
    task_paths = os.listdir(os.path.join(base_folder, file))
    task_score = defaultdict(list)
    task_paths = [path for path in task_paths if os.path.isdir(os.path.join(base_folder, file, path))]
    for task_path in task_paths:
        taskname = os.path.basename(task_path).split("_")[0]
        result_path = os.path.join(base_folder, file, task_path, "results.jsonl")
        if not os.path.exists(result_path):
            continue
        with jsonlines.open(result_path) as reader:
            for line in reader:
                score = line["is_successful"]
                #if "exception_info" in line and line["exception_info"] is not None:
                #    print(taskname)
                #    print(line["exception_info"])
        if np.isnan(score):
            continue
        
        task_score[taskname].append(score)
    score_line = []
    # 同时创建一个dataframe，两列分别是taskname和mean_score
    task_df_data = []
    for taskname, scores in task_score.items():
        if len(scores) == 0:
            continue
        mean_score = sum(scores) / len(scores)
        if not np.isnan(mean_score):
            score_line.append(mean_score)
            task_df_data.append({
                'taskname': taskname,
                'mean_score': mean_score
            })
    task_df = pd.DataFrame(task_df_data)
            
    if sum(score_line) / 116 < 0.2:
        continue
    # 把以下内容加到all_results中，然后按照score从大到小排序
    all_results.append([model_name, sum(score_line) / 116, len(score_line), task_df])

all_results = sorted(all_results, key=lambda x: x[1], reverse=True)
# 以方便阅读的格式输出
for result in all_results:
    print(f"Model: {result[0]}, Success Rate: {result[1]:.2%}, Num of Tasks: {result[2]}")


df = pd.read_excel("/raid/xuyifan/Android-Lab-main/evaluation/android_world/android_world_results.xlsx")

# 对每个模型的结果进行处理
for result in all_results:
    model_name = result[0]
    task_df = result[3]
    
    # 将task_df的taskname与df的task_template对应
    # 使用merge而不是join以保持df的原始顺序
    df = df.merge(task_df.rename(columns={
        'taskname': 'task_template',
        'mean_score': model_name
    })[['task_template', model_name]], 
    on='task_template', 
    how='left')

# 将结果保存到新的Excel文件，转置存储
df.to_excel("/raid/xuyifan/Android-Lab-main/logs/android_world/android_world_results_with_models.xlsx")


