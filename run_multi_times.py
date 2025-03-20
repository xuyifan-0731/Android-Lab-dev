import os
import json
import jsonlines
from typing import List, Dict, Any
import time


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    data = []
    try:
        with jsonlines.open(file_path, 'r') as reader:
            for item in reader:
                data.append(item)
    except Exception as e:
        print(f"Error loading jsonl file {file_path}: {e}")
    
    return data

start_time = time.time()
all_wrong = []
all_complete_correct = []
for i in range(10):
    # os.system(f"rm -rf logs/shudan/qwen25-vl-v4-fa2-ep4-{i+1}")
    # os.system(f"rm -rf outputs_shudan/qwen25-vl-v4-fa2-ep4-{i+1}_*")
    os.system("docker ps -a --filter 'ancestor=android_eval:v2' -q | xargs -r docker rm -f")
    
    os.system(f"python eval.py -n qwen25-vl-v4-fa2-ep4-{i+1} -c /raid/xuyifan/Android-Lab-xml/Android-Lab-main/configs/shudan/qwen2-vl-v4.yaml -p 20 && python generate_result.py")
    
    result_files = os.listdir("outputs_shudan")
    result_files = [file for file in result_files if file.startswith(f"qwen25-vl-v4-fa2-ep4-{i+1}_2025")]
    
    result = load_jsonl(f"outputs_shudan/{result_files[0]}/results.jsonl")
    wrong = [item for item in result if "complete" not in item["result"] or item["result"]["complete"] == False]
    wrong.sort(key=lambda x: x["task_id"])
    all_wrong.append([item["task_id"] for item in wrong])
    
    total = load_jsonl(f"outputs_shudan/{result_files[0]}/total.jsonl")
    correct = sum([item['Complete_Correct'] for item in total])
    complete_correct = correct / 138
    all_complete_correct.append(complete_correct)

for wrong, complete_correct in zip(all_wrong, all_complete_correct):
    print(f"Run qwen25-vl-v4-fa2-ep4-{i+1}:")
    print(f"Wrong: {wrong}, Complete Correct: {complete_correct}")
    print("-"*100)

end_time = time.time()
print(f"Total time: {end_time - start_time} seconds")