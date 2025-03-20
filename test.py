import json

def load_jsonl(path, encoding='utf-8'):
    res = []
    with open(path, encoding=encoding) as f:
        for line in f:
            res.append(json.loads(line))
    return res


result1 = load_jsonl('/raid/xuyifan/Android-Lab-xml/Android-Lab-main/outputs_shudan/glm-v4-nodesc-ocr_w_ocr_train_2024-12-24-00-56-12/results.jsonl')
wrong_task1 = [task['task_id'] for task in result1 if not task.get('result', {}).get('complete', True)]
print(len(wrong_task1))
print(f"Wrong Task1: ", wrong_task1)

result2 = load_jsonl('/raid/xuyifan/Android-Lab-xml/Android-Lab-main/outputs_shudan/glm-v4-nodesc_2024-12-23-02-40-34/results.jsonl')
wrong_task2 = [task['task_id'] for task in result2 if not task.get('result', {}).get('complete', True)]
print(len(wrong_task2))
print(f"Wrong Task2: ", wrong_task2)

wrong_task1 = set(wrong_task1)
wrong_task2 = set(wrong_task2)

only_in_task1 = wrong_task1 - wrong_task2
only_in_task2 = wrong_task2 - wrong_task1

print(f"Diff Task1: ", only_in_task1)
print(f"Diff Task2: ", only_in_task2)

