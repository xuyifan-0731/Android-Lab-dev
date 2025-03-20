import os
import shutil
import jsonlines

folder = "/raid/xuyifan/Android-Lab-xml/Android-Lab-main/logs/shudan"
files = os.listdir(folder)


for file in files:
    if file == ".DS_Store" or file == "emulator_output.txt":
        continue
    tasks = os.listdir(os.path.join(folder, file))
    for task in tasks:
        if task == ".DS_Store":
            continue
        if not os.path.exists(os.path.join(folder, file, task, "traces/trace.jsonl")):
            print(f"Trace for task '{file, task}' not found.")
            if os.path.exists(os.path.join(folder, file, task)):
                shutil.rmtree(os.path.join(folder, file, task))
        else:
            try:
                with jsonlines.open(os.path.join(folder, file, task, "traces/trace.jsonl")) as reader:
                    traces = list(reader)
                if len(traces) == 0:
                    print(f"Task '{file, task}' has empty trace.")
                    if os.path.exists(os.path.join(folder, file, task)):
                        shutil.rmtree(os.path.join(folder, file, task))
                    continue
                if "finish" in traces[-1]["current_response"]:
                    continue
                else:
                    if len(traces) > 1 and traces[-1]["current_response"] != traces[-2]["current_response"]:
                        continue
                    else:
                        print(f"Task '{file, task}' has unfinish trace.")
                        if os.path.exists(os.path.join(folder, file, task)):
                            shutil.rmtree(os.path.join(folder, file, task))
            except:
                print(f"Error in task '{file, task}'.")
                if os.path.exists(os.path.join(folder, file, task)):
                    shutil.rmtree(os.path.join(folder, file, task))

            #import pdb; pdb.set_trace()
            
