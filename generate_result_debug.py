import argparse
import concurrent.futures
import datetime
import os
import shutil
from collections import defaultdict
from glob import glob
from os.path import join, isdir, isfile, relpath
from typing import List, Dict

import jsonlines
import pandas as pd

from evaluation.configs import AppConfig
from evaluation.task import Evaluation_Task


# from generate_result_single import *


def find_all_task_files(all_task_config_path) -> List[str]:
    # print(type(all_task_config_path), all_task_config_path)
    tasks = []
    for task in all_task_config_path:
        if isdir(task):
            tasks += [relpath(path, ".") for path in glob(join(task, "**/*.yaml"), recursive=True)]
        elif isfile(task):
            tasks.append(task)
        else:
            print(f"'{task}' is not a valid file or directory, ignored.")
    return tasks


def find_all_traces_files(traces_path_fold) -> Dict[str, Dict[str, str]]:
    # print(type(all_task_config_path), all_task_config_path)
    traces_path = os.listdir(traces_path_fold)
    traces = {}
    for trace in traces_path:
        app_name = trace.split('_')[0]
        app_id = trace.split('_')[1]
        task_id = f"{app_name}_{app_id}"
        trace_root = os.path.join(traces_path_fold, trace)
        trace_file = os.path.join(trace_root, "traces", "trace.jsonl")
        xml_path = os.path.join(trace_root, "xml")
        trace_item = {
            "task_id": task_id,
            "trace_file": trace_file,
            "xml_path": xml_path,
            "trace_root": trace_root
        }
        traces[task_id] = trace_item
    return traces


def evaluate_all_tasks(tasks: List[Evaluation_Task]):
    for task in tasks:
        try:
            task.evaluate()
            del task
        except Exception as e:
            import traceback
            print(traceback.format_exc())


def evaluate_input_dir(input_dir, task_yamls, create_time, args):
    test_name = input_dir.split('/')[-1]
    output_root_dir = os.path.join(args.output_folder, test_name + "_" + create_time)
    if not os.path.exists(output_root_dir):
        os.makedirs(output_root_dir)

    task_files = find_all_task_files(task_yamls)
    traces = find_all_traces_files(input_dir)

    tasks = []
    print("> Loading task configs")
    for app_task_config_path in task_files:
        app_config = AppConfig(app_task_config_path, output_dir=output_root_dir)
        app_task = Evaluation_Task(app_config, traces, args, detail=True)
        if "task_id" in args and len(args.task_id) > 0:
            app_task.task_list_delete(args.task_id)
        if args.debug:
            app_task.task_list_delete(args.task_id)
        print(f"    Evaluation_Task '{app_task.name}' loaded from config {app_task_config_path}")
 
        tasks.append(app_task)

    print(f"> Successfully load {len(tasks)} task{'s' if len(tasks) > 1 else ''}")
    evaluate_all_tasks(tasks)


def output_to_excel(args):
    output_df = pd.DataFrame()
    base_folder = args.output_folder
    outputs = os.listdir(base_folder)

    for output in outputs:
        output_folder = os.path.join(base_folder, output)
        agent_name = output.split("_2024")[0]
        if not os.path.exists(os.path.join(output_folder, "total.jsonl")):
            continue
        with jsonlines.open(os.path.join(output_folder, "total.jsonl")) as f:
            dict = defaultdict(list)
            tt = 0
            for line in f:
                # total = line["Total"]
                # App = line["App"]
                for key, value in line.items():
                    if key == "App":
                        dict["App"].append(1)
                    elif key == "Total":
                        dict[key].append(value)
                        tt += value
                    elif "Sum_" in key or key == "Complete_Correct":
                        dict[key].append(value)
            tt_correct = sum(dict["Complete_Correct"])
            output_dict = {}
            output_dict["agent_name"] = agent_name
            for key, value in dict.items():
                if key == "App":
                    output_dict[key] = len(value)
                elif key == "Total":
                    output_dict[key] = sum(value)
                elif key == "Sum_RRR":
                    if tt_correct == 0:
                        output_dict[key] = 0
                    else:
                        output_dict[key] = 100 * sum(value) / tt_correct
                elif key == "Complete_Correct" or "Sum_" in key:
                    output_dict[key] = 100 * sum(value) / args.tt
                # else:
                # output_dict[key] = sum(value) / tt
            print(output_dict)
            # output_dict["Acc"] = output_dict["Complete_Correct"] / output_dict["Total"]
            output_dict["Acc"] = tt_correct / tt
            output_dict["correct"] = tt_correct
            output_df = output_df._append(output_dict, ignore_index=True)
    output_df.to_excel(args.output_excel)
    print(output_df)
    return output_df


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_argument_group("evaluation", "Evaluation configurations")
    group.add_argument("--input_folder", type=str, default="/raid/xuyifan/Android-Lab-xml/Android-Lab-main/logs/shudan")
    group.add_argument("--output_folder", type=str, default="outputs_debug")
    group.add_argument("--output_excel", type=str, default="output.xlsx")
    group.add_argument("--tt", type=int, default=138)
    group.add_argument("--judge_model", type=str, default="glm4")
    group.add_argument("--api_base", type=str, default="")
    group.add_argument("--api_key", type=str, default="a9e4c4bc2c3c8f5b026ec10488b7b485.SZHOUgvPfCEKbztk")
    group.add_argument("--model_name", type=str, nargs="+", required=True)
    group.add_argument("--task_id", type=str, nargs="+", required=True)
    group.add_argument("--debug", action="store_true", default=False)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    assert args.judge_model in ["glm4", "gpt-4o-2024-05-13"], "We only support glm4 or gpt-4o for judge model"
    task_yamls = os.listdir('evaluation/config')
    task_yamls = ["evaluation/config/" + i for i in task_yamls if i.endswith(".yaml")]
    create_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    input_folder = args.input_folder

    input_dirs = [os.path.join(input_folder, input_dir) for input_dir in os.listdir(input_folder)]
    model_dirs = []
    for input_dir in input_dirs:
        model_name = input_dir.split('/')[-1]
        if model_name in args.model_name:
            model_dirs.append(input_dir)

    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)
    else:
        shutil.rmtree(args.output_folder)
        os.makedirs(args.output_folder)


    test_agents = []
    for input_dir in model_dirs:
        if "emulator_output.txt" in input_dir:
            continue
        test_agents.append(input_dir)

    # no parrallel
    for input_dir in test_agents:
        evaluate_input_dir(input_dir, task_yamls, create_time, args)
    '''

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(evaluate_input_dir, input_dir, task_yamls, create_time, args) for input_dir in
                   test_agents]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                import traceback
                traceback.print_exc()
                print(f'Generated an exception: {exc}')'''
    output_df_main_result = output_to_excel(args)
    output_df_app_result = pd.DataFrame()
    files = os.listdir(args.output_folder)
    for file in files:
        output_folder = os.path.join(args.output_folder, file)
        agent_name = file.split("_2024")[0]
        if "test" in agent_name:
            continue
        if not os.path.exists(os.path.join(output_folder, "total.jsonl")):
            continue
        output_dict = {"agent_name": agent_name}
        with jsonlines.open(os.path.join(output_folder, "total.jsonl")) as f:
            for line in f:
                app = line["App"]
                correct = line["Complete_Correct"]
                output_dict[app] = correct
        #if output_dict["agent_name"] in test_agents:
            #print("Add result: ", output_dict)
        output_df_app_result = output_df_app_result._append(output_dict, ignore_index=True)

    #desired_order = ["bluecoins", "calendar", "cantook", "clock", "contacts", "map", "pimusic", "setting", "zoom"]
    #output_df_app_result = output_df_app_result[["agent_name"] + desired_order]
    merged_df = pd.merge(output_df_main_result, output_df_app_result, on="agent_name")
    merged_df.to_excel(args.output_excel.replace(".xlsx", "_detail.xlsx"))


if __name__ == "__main__":
    main()
