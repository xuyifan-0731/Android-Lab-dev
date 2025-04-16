from queue import Queue
import concurrent
from evaluation.auto_test import *
from evaluation.android_world_utils import AndroidWorld_Sample


def task_done_callback(future, docker_instance, free_dockers):
    free_dockers.put(docker_instance)


def parallel_worker(class_, config, parallel, tasks):
    free_dockers = Queue()
    for idx in range(parallel):
        if config.docker:
            instance = Docker_Instance(config, idx)
        elif config.android_world:
            instance = Instance_AndroidWorld(config, idx)
        else:
            instance = Instance(config, idx)
        free_dockers.put(instance)

    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
        while tasks:
            if free_dockers.empty():
                time.sleep(0.5)
                continue

            instance = free_dockers.get()
            task = tasks.pop(0)

            config_copy = copy.deepcopy(config)
            auto_class = class_(config_copy)

            future = executor.submit(auto_class.run_task, task, instance)
            future.add_done_callback(lambda fut, di=instance: task_done_callback(fut, di, free_dockers))

def task_done_callback_android_world(future, instance, free_dockers, results):
    try:
        result = future.result()
        if result:
            results.extend(result)
    except Exception as e:
        print(f"Task failed with exception: {e}")
    finally:
        free_dockers.put(instance)

def parallel_worker_android_world(args, class_, AndroidWorld_AutoTest, config, agent, parallel, tasks, sample = False):
    free_dockers = Queue()
    results = []
    if isinstance(tasks, dict):
        items = list(tasks.items())
        tasks = [dict(items[i:i + 1]) for i in range(0, len(items), 1)]
    

    #for idx in range(parallel):
        #from evaluation.android_world_utils import Instance_AndroidWorld_docker
        #instance = Instance_AndroidWorld_docker(config, idx, args.parallel_start_num)
        #free_dockers.put(instance)
    for idx in range(parallel):
        free_dockers.put(idx)
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
        while tasks:
            if free_dockers.empty():
                time.sleep(0.5)
                continue

            #instance = free_dockers.get()
            idx = free_dockers.get()
            task = tasks.pop(0)
            config_copy = copy.deepcopy(config)
            #agent_copy = copy.deepcopy(agent)
            auto_class = class_(config_copy)
            android_world_class = AndroidWorld_AutoTest(config_copy, auto_class, agent, idx, args.parallel_start_num)
            future = executor.submit(android_world_class.run_task, task)
            future.add_done_callback(lambda fut, di=idx: task_done_callback_android_world(fut, di, free_dockers, results))
            '''
            if not sample:
                android_world_class = AndroidWorld_AutoTest(config_copy, auto_class, agent)
                future = executor.submit(android_world_class.run_task, task, instance)
                future.add_done_callback(lambda fut, di=instance: task_done_callback_android_world(fut, di, free_dockers, results))
            else:
                android_world_class = AndroidWorld_Sample(config_copy, auto_class, agent)
                future = executor.submit(android_world_class.android_world_task_wrapper, task, instance)
                future.add_done_callback(lambda fut, di=instance: task_done_callback_android_world(fut, di, free_dockers, results))'''
    
    return results
