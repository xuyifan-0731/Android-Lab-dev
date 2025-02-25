from collections.abc import Sequence
import os
import time
import random
import datetime
import subprocess
import jsonlines

from absl import app
from absl import flags
from absl import logging
from android_world import checkpointer as checkpointer_lib
from android_world import registry
from android_world import suite_utils
from android_world.suite_utils import process_episodes
from android_world.agents import base_agent
from android_world.agents import human_agent
from android_world.agents import infer
from android_world.agents import m3a
from android_world.agents import random_agent
from android_world.agents import seeact
from android_world.agents import t3a
from android_world.env import env_launcher
from android_world.env import interface
from android_world.env import adb_utils
from android_world.env import json_action

from evaluation.auto_test import AutoTest, Instance_AndroidWorld
from evaluation.evaluation import *
from evaluation.auto_test import find_package
from recorder import JSONRecorder
from evaluation.docker_utils import create_docker_container, execute_command_in_container, remove_docker_container, \
    start_avd, stop_avd

def split_dict(input_dict, n = 1):
    if not isinstance(input_dict, dict) or not isinstance(n, int) or n <= 0:
        raise ValueError("输入参数不合法，input_dict 应为字典，n 应为正整数")
    
    items = list(input_dict.items())
    return [dict(items[i:i + n]) for i in range(0, len(items), n)]

_TASKS = None
_FIXED_TASK_SEED = False
_TASK_RANDOM_SEED = 30
_N_TASK_COMBINATIONS = 1
_EMULATOR_SETUP = False
_SUITE_FAMILY = registry.TaskRegistry.ANDROID_WORLD_FAMILY
# other:registry.TaskRegistry.MINIWOB_FAMILY_SUBSET
  
def turn_on_ac(state, env):
    x = None
    y = None
    for ui_element in state.ui_elements:
        if ui_element.content_description == "XMLParser（数据标注）":
            bbox_pixels = ui_element.bbox_pixels
            x = (bbox_pixels.x_min + bbox_pixels.x_max) / 2
            y = (bbox_pixels.y_min + bbox_pixels.y_max) / 2
            break
    if x is not None and y is not None:
        action = json_action.JSONAction(**{'action_type':'click', 'x':x,'y':y})
        env.execute_action(action)
        time.sleep(2)
    else:
        return None

def print_android_world_results(path = None, all_results = None):
    if path is not None and all_results is None:
        task_paths = os.listdir(path)
        all_results = []
        for task_path in task_paths:
            if not os.path.exists(os.path.join(path, task_path, "results.jsonl")):
                continue
            with jsonlines.open(os.path.join(path, task_path, "results.jsonl"), "r") as reader:
                for line in reader:
                    all_results.append(line)
    df = process_episodes(all_results, print_summary = True)
    df.to_excel(os.path.join(path, "results.xlsx"), index=True)
    return df

class AndroidLabAgent(base_agent.EnvironmentInteractingAgent):
  """A random agent interaction loop for testing purposes."""

  def __init__(
      self,
      env: interface.AsyncEnv,
      name: str = 'AndroidLabAgent',
      verbose: bool = False,
      autotest_agent: AutoTask | None = None,
      max_rounds: int = 15,
      app: str = None,
      controller: AndroidController | None = None,
  ):
    """Initializes a RandomAgent.

    Args:
      env: The environment.
      name: The agent name.
      verbose: True if the grounder should produce verbose updates.
    """
    super().__init__(env, name)
    self.env = env
    self._verbose = verbose
    self.autotest_agent = autotest_agent
    self.max_rounds = max_rounds
    self.app = app
    self.controller = controller

  def step(self, goal: str) -> base_agent.AgentInteractionResult:
    """See base class."""
    round_count = self.autotest_agent.record.get_round_count()
    if round_count == 0:
        print("launch app: ", find_package(self.app))
        self.controller.launch_app(find_package(self.app))
        time.sleep(5)
    
    state = self.get_post_transition_state()
    if round_count == 0 and not self.autotest_agent.controller.check_ac_survive():
        turn_on_ac(state, self.env)
        self.autotest_agent.accessibility = self.autotest_agent.controller.check_ac_survive()

    self.autotest_agent.run_step()
    
    step_data = {
        'raw_screenshot': state.pixels,
        'ui_elements': state.ui_elements,
    }
    # TODO: 需要修改done的判断: finish or early stop
    done = False
    if self.autotest_agent.page_executor.is_finish:
        done = True
        self.autotest_agent.page_executor.update_screenshot(prefix="end")

    
    if round_count >= self.max_rounds:
        done = True
        
    return base_agent.AgentInteractionResult(
        done,
        step_data,
    )

def initialize_android_world_suite():
    n_task_combinations = _N_TASK_COMBINATIONS
    task_registry = registry.TaskRegistry()
    suite = suite_utils.create_suite(
        task_registry.get_registry(family=_SUITE_FAMILY),
        n_task_combinations=n_task_combinations,
        seed=_TASK_RANDOM_SEED,
        tasks=_TASKS,
        use_identical_params=_FIXED_TASK_SEED,
    )
    suite.suite_family = _SUITE_FAMILY
    return suite

'''
class Docker_Instance_AndroidWorld(Docker_Instance):
    def initialize_worker(self, config):
        self.config = config
        print_with_color(f"Starting Android Emulator in docker with AVD name: {config.avd_name}", "blue")
        if "local_port" in self.config.docker_args:
            local_port_start = self.config.docker_args["local_port"]
        else:
            local_port_start = 6060
        docker_port_local = find_free_ports(start_port=local_port_start + self.idx)
        self.docker_port_local = docker_port_local
        self.device_port = docker_port_local
        print(f"Local port: {docker_port_local}")
        grpc_prot_start = docker_port_local + 50
        grpc_port_loacl = find_free_ports(start_port=grpc_prot_start)
        self.grpc_port_loacl = grpc_port_loacl
        self.grpc_port = 8554
        print(f"GRPC port: {grpc_port_loacl}")

    def start_docker(self, docker_image_name, docker_port):
        container_id = create_docker_container(docker_image_name, [(docker_port, self.docker_port_local), (self.grpc_port, self.grpc_port_loacl)])
        return container_id
'''

class AndroidWorld_AutoTest(AutoTest):
    def __init__(self, config, base_class, llm_agent) -> None:
        self.config = config
        self.base_class = base_class
        self.llm_agent = llm_agent
        #self.test_llm_agent()

    def test_llm_agent(self):
        print("test_llm_agent")
        print(self.llm_agent)
        print("input: hello, who are you?")
        response = self.llm_agent.act(messages=[{"role": "user", "content": "hello, who are you?"}])
        print(response)

    def start_emulator(self, instance):
        if self.config.docker:
            type = "docker"
        else:
            type = "cmd"
        device = instance.initialize_single_task(self.config)
        #adb_path = _find_adb_directory(self.config.adb_path)
        adb_path = self.config.adb_path
        env = env_launcher.load_and_setup_env(
            console_port=instance.device_port,
            emulator_setup=_EMULATOR_SETUP,
            adb_path=adb_path,
            grpc_port=instance.grpc_port
        )

        self.env = env

        self.controller = AndroidController(device, type, instance)


    def run_serial(self, tasks):
        #if self.config.docker:
            #instance = Docker_Instance_AndroidWorld(self.config)
        #else:
        instance = Instance_AndroidWorld(self.config)

        tasks = split_dict(tasks, 1)
        #for task in tasks:
            #if "ContactsAddContact" == list(task.keys())[0]:
                #self.run_task(task, instance)


        #random_task = random.choice(tasks)
        #self.run_task(random_task, instance)
        #task = tasks[0]
        #self.run_task(task, instance)
        for task in tasks:
            self.run_task(task, instance)

    def run_task(self, suite, instance):
        task_id = list(suite.keys())[0]
        app = suite[task_id][0].app_names[0]
        self.instruction = suite[task_id][0].goal
        self.base_class.instruction = self.instruction
        self.command_per_step = None
        self.base_class.command_per_step = self.command_per_step
        self.app = app

        demo_timestamp = int(time.time())
        self.config.task_name = task_id + "_" + datetime.datetime.fromtimestamp(demo_timestamp).strftime(
            "%Y-%m-%d_%H-%M-%S")
        
        self.prepare_for_task()
        self.start_emulator(instance)
 
        self.config.checkpoint_dir = os.path.join(self.config.task_dir, "android_world_checkpoint")
        checkpoint_dir = checkpointer_lib.create_run_directory(self.config.checkpoint_dir)

        print(
            f'Starting eval with agent and writing to'
            f' {checkpoint_dir}'
        )

        # TODO: 为了适配原有的构造prompt方法，需要拆解_run_task_suite，使得构造的prompt最终能够被传入agent.step
        # 为了最大限度兼容，目前思路是把AutoTask()类整个传入androidlab agent（对应的应该在agent.llm传入调用部分，在agent.step中调用autotask()
        
        # suite_utils.run中可以运行多个任务，但是这里需要保证一次只运行一个任务，才能与原来的设定autotest对齐
        assert len(suite) == 1, "Only one task is supported for now"
        self.base_class.controller = self.controller
        self.base_class.config = self.config
        
        self.page_executor = self.get_executor()
        self.base_class.page_executor = self.page_executor
        self.record = JSONRecorder(id=self.config.task_name, instruction=self.instruction,
                                   page_executor=self.page_executor,
                                   config=self.config)
        self.base_class.record = self.record
        self.base_class.llm_agent = self.llm_agent
        self.autotest_agent = self.get_agent()

        #agent = _get_agent(self.env, autotest_agent = self.autotest_agent, max_rounds=self.config.max_rounds)
        agent = AndroidLabAgent(self.env, autotest_agent=self.autotest_agent, max_rounds=self.config.max_rounds, app=self.app, controller=self.controller)
        agent.name = "AndroidLabAgent"

        results = suite_utils.run(
            suite,
            agent,
            checkpointer=checkpointer_lib.IncrementalCheckpointer(checkpoint_dir),
            demo_mode=False,
        )

        with jsonlines.open(os.path.join(self.config.task_dir, "results.jsonl"), "a") as writer:
            writer.write_all(results)

        self.env.close()
        instance.stop_single_task()

        return results

    def get_agent(self):
        return self.base_class.get_agent()

    def get_executor(self):
        return self.base_class.get_executor()
