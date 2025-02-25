import os
import shutil
import jsonlines
from templates.packages import find_package

def check_invalid(file, all_task_start_info = None):
    file_check = {}
    file_path = {}
    tasks = os.listdir(os.path.join(file))
    for task in tasks:
        if task == ".DS_Store":
            continue
        task_clean = task.split("_")[0] + "_" + task.split("_")[1]
        if task.split("_")[0] == "general":
            task_clean = task.split("_")[0] + "_" + task.split("_")[1] + "_" + task.split("_")[2]

        file_check[task_clean] = True
        file_path[task_clean] = os.path.join(file, task)
        if all_task_start_info is not None:
            if task_clean not in all_task_start_info:
                continue
            package = find_package(all_task_start_info[task_clean]["app"])
        else:
            package = None
        
        if not os.path.exists(os.path.join(file, task, "traces/trace.jsonl")):
            print(f"Trace for task '{file, task}' not found.")
            file_check[task_clean] = False
        else:
            try:
                with jsonlines.open(os.path.join(file, task, "traces/trace.jsonl")) as reader:
                    traces = list(reader)
                if len(traces) == 0:
                    print(f"Task '{file, task}' has empty trace.")
                    file_check[task_clean] = False
                    continue
                if package is not None and traces[0]["current_activity"] != package:
                    print(f"Task '{file, task}' was not begin correctly.")
                    file_check[task_clean] = False
                    continue
                if "finish" in traces[-1]["current_response"]:
                    continue
                else:
                    if len(traces) > 1 and traces[-1]["current_response"] != traces[-2]["current_response"]:
                        continue
                    else:
                        print(f"Task '{file, task}' has unfinish trace.")
                        file_check[task_clean] = False
                xml_files = os.listdir(os.path.join(file, task, "xml"))
                for xml in xml_files:
                    if not xml.endswith("compressed_xml.txt"):
                        continue
                    with open(os.path.join(file, task, "xml", xml), "r") as f:
                        content = f.read()
                        if "ERR_CONNECTION_CLOSED" in content:
                            print(f"Task '{file, task}' has error in web.")
                            file_check[task_clean] = False
            except:
                print(f"Error in task '{file, task}'.")
                file_check[task_clean] = False
    return file_check, file_path

        