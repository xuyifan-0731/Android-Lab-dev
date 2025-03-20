import os
import random
import jsonlines
from collections import defaultdict
correct = defaultdict(list)
base_path = "/raid/xuyifan/Android-Lab-main/outputs"
model_result_file = os.listdir(base_path)
model_result_file = [os.path.join(base_path, file, "results.jsonl") for file in model_result_file if "lama3.1-8b-v26-xmlv2-full-3e" in file]
for file in model_result_file:
    with jsonlines.open(file) as reader:
        for obj in reader:
            try:
                correct[obj["task_id"]].append(obj["result"]["complete"])
            except:
                correct[obj["task_id"]].append(False)

for k in range(1,20):
    tt = 0
    tt_correct = 0
    for task_id, value in correct.items():
        value = random.sample(value, k)
        if True in value:
            tt_correct += 1
        tt += 1
    print(f"Top {k} accuracy: {tt_correct / tt}")
