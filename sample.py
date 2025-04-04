from evaluation.auto_test import *
from evaluation.parallel import parallel_worker
from generate_result_single import find_all_task_files
import argparse
import yaml
from evaluation.configs import AppConfig_Sample
from check_invaild_trace import check_invalid


def generate_info(task_files):
    all_task_start_info = {}
    for app_task_config_path in task_files:
        app_config = AppConfig_Sample(app_task_config_path)
        if args.task_id is None:
            task_ids = list(app_config.task_name.keys())
        else:
            task_ids = args.task_id

        for task_id in task_ids:
            #if task_id in already_run:
                #print(f"Task {task_id} already run, skipping")
                #continue
            if task_id not in app_config.task_name:
                #print(f"Task {task_id} not found in config, skipping")
                continue
            task_instruction = app_config.task_name[task_id].strip()
            app = app_config.APP
            if args.app is not None:
                if app not in args.app:
                    continue
            if single_config.mode == "in_app":
                package = app_config.package

                if "general" in app_config.file_path:
                    task_instruction = task_instruction
                else:
                    task_instruction = f"You should use {app} to complete the following task: {task_instruction}"
            else:
                package = None
                command_per_step = None
            all_task_start_info[task_id] = {
                "agent": agent,
                "task_id": task_id,
                "task_instruction": task_instruction,
                "package": package,
                "app": app
            }
            #print(f"Task {task_id} added to run queue")
    return all_task_start_info


if __name__ == '__main__':
    task_yamls = os.listdir('evaluation/config-sample/')
    task_yamls = ["evaluation/config-sample/" + i for i in task_yamls if i.endswith(".yaml")]
    #task_yamls = ["evaluation/config-sample/web_shopping.yaml"]
    #task_yamls = ["evaluation/config-sample/chorme.yaml"]


    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-n", "--name", default="test", type=str)
    arg_parser.add_argument("-c", "--config", default="config-mllm-0409.yaml", type=str)
    arg_parser.add_argument("--task_config", nargs="+", default=task_yamls, help="All task config(s) to load")
    arg_parser.add_argument("--task_id", nargs="+", default=None)
    arg_parser.add_argument("--debug", action="store_true", default=False)
    arg_parser.add_argument("--app", nargs="+", default=None)
    arg_parser.add_argument("-p", "--parallel", default=1, type=int)
    #arg_parser.add_argument("-auto","--auto_resample", action="store_true", default=False)
    arg_parser.add_argument("-e", "--epoch", default=3, type=int)

    args = arg_parser.parse_args()
    for idx in range(args.epoch):
        print(f"Epoch {idx+1}")
        name = f"{args.name}_r{idx+1}"

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

        task_files = find_all_task_files(args.task_config)
        all_task_start_info = generate_info(task_files)
        
        already_run = []
        log_path = single_config.subdir_config(name).save_dir
        if os.path.exists(log_path):
            file_check, file_paths = check_invalid(log_path, all_task_start_info)
            for key, value in file_check.items():
                if value:
                    already_run.append(key)
                else:
                    #print(f"Task '{key}' is invalid.")
                    file_path = file_paths[key]
                    #if os.path.exists(file_path):
                        #shutil.rmtree(file_path)
        #print(f"Already run: {already_run}")
        print(f"Already run num: {len(already_run)}")
        
        run_task_start_info = []
        for key, value in all_task_start_info.items():
            if key in already_run:
                pass
                #print(f"Task '{key}' already run, skipping")
            else:
                run_task_start_info.append(value)
                #print(f"Task '{key}' added to run queue")
        
        print(f"Task to run: {len(run_task_start_info)}")
        info = {
            "epoch": args.epoch,
            "now_epoch": idx+1,
            "task_num": len(run_task_start_info),
            "now_log_path": log_path.split("/")[-1]
        }
        with open(log_path.replace(log_path.split("/")[-1], "info.json"), "w") as f:
            json.dump(info, f)
        if len(run_task_start_info) == 0:
            print("No task to run")
            break
     
        class_ = globals().get(autotask_class)

        if len(run_task_start_info) <= args.parallel:
            args.parallel = len(run_task_start_info)
        if args.parallel == 0:
            raise ValueError("Parallel should be greater than 0")
        
        if class_ is None:
            raise AttributeError(f"Class {autotask_class} not found. Please check the class name in the config file.")
        single_config.sample = True
        if args.parallel == 1:
            Auto_Test = class_(single_config.subdir_config(name))
            Auto_Test.run_serial(run_task_start_info)
        else:
            parallel_worker(class_, single_config.subdir_config(name), args.parallel, run_task_start_info)



