import os
import jsonlines
import argparse
import yaml

from agent import get_agent
from evaluation.auto_test import *
from evaluation.android_world_utils import AndroidWorld_AutoTest, initialize_android_world_suite, print_android_world_results, split_dict
from evaluation.parallel import parallel_worker, parallel_worker_android_world
from generate_result import find_all_task_files
from evaluation.configs import AppConfig, TaskConfig

try:
    from evaluation.android_world import *
except:
    print("Android World is not installed")


if __name__ == '__main__':
    # 将当前路径的tmp文件设置为os.environ['TMPDIR']
    os.environ['TMPDIR'] = os.path.join(os.getcwd(), 'tmp')
    if not os.path.exists(os.environ['TMPDIR']):
        os.makedirs(os.environ['TMPDIR'])
    
    task_yamls = os.listdir('evaluation/config')
    task_yamls = ["evaluation/config/" + i for i in task_yamls if i.endswith(".yaml")]

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-n", "--name", default="test", type=str)
    arg_parser.add_argument("-d", "--dataset", default="android_lab", type=str)
    arg_parser.add_argument("-c", "--config", default="config-mllm-0409.yaml", type=str)
    arg_parser.add_argument("--task_config", nargs="+", default=task_yamls, help="All task config(s) to load")
    arg_parser.add_argument("--task_id", nargs="+", default=None)
    arg_parser.add_argument("--debug", action="store_true", default=False)
    arg_parser.add_argument("--app", nargs="+", default=None)
    arg_parser.add_argument("--n_task_combinations", default=1, type=int)
    arg_parser.add_argument("--random", action="store_true", default=False)
    arg_parser.add_argument("-p", "--parallel", default=1, type=int)
    arg_parser.add_argument("--ir_only", action="store_true", default=False)
    arg_parser.add_argument("--parallel_start_num", default=0, type=int)

    args = arg_parser.parse_args()

    assert args.dataset in ["android_lab", "android_world"], "Invalid dataset, please choose from android_lab or android_world"
    with open(args.config, "r") as file:
        yaml_data = yaml.safe_load(file)

    agent_config = yaml_data["agent"]
    task_config = yaml_data["task"]
    eval_config = yaml_data["eval"]

    autotask_class = task_config["class"] if "class" in task_config else "ScreenshotMobileTask_AutoTest"

    single_config = TaskConfig(**task_config["args"])
    single_config = single_config.add_config(eval_config)
    if "True" == agent_config.get("relative_bbox"):
        single_config.is_relative_bbox = True
    agent = get_agent(agent_config["name"], **agent_config["args"])
    already_run = []
    if args.n_task_combinations == 1:
        if os.path.exists(os.path.join(single_config.save_dir, args.name)):
            already_run = os.listdir(os.path.join(single_config.save_dir, args.name))
            already_run = [i.split("_")[0] for i in already_run]
    

    all_task_start_info = []
    if args.random:
        suite = initialize_android_world_suite(n_task_combinations = args.n_task_combinations, seed = None, task_template = args.task_id)
    else:
        suite = initialize_android_world_suite(n_task_combinations = args.n_task_combinations, seed = 30, task_template = args.task_id)
    if not args.task_id:
        num_delete = 0
        for key in already_run:
            if key in suite:
                del suite[key]
                num_delete += 1
                print(f"Task {key} already run, skipping")
        print(f"Num of tasks already run: {num_delete}")
    suite_list = split_dict(suite, 1)
    class_ = globals().get(autotask_class)
    if class_ is None:
        raise AttributeError(f"Class {autotask_class} not found. Please check the class name in the config file.")
    Auto_Test = class_(single_config.subdir_config(args.name))
    task_path = os.path.join(single_config.save_dir, args.name)
    args.parallel = min(args.parallel, len(suite_list))
    if args.parallel == 1:
        android_world_class = AndroidWorld_AutoTest(single_config.subdir_config(args.name), Auto_Test, agent)
        android_world_class.run_serial(suite_list)
        print_android_world_results(path = task_path)
    else:
        results = parallel_worker_android_world(args, class_, AndroidWorld_AutoTest, single_config.subdir_config(args.name), agent, args.parallel, suite_list)
        print(results)
        print_android_world_results(path = task_path, all_results = results)


