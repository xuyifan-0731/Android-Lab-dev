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
#from android_world.env import env_launcher
from evaluation.android_world_load import load_and_setup_env
from android_world.env import interface
from android_world.env import adb_utils
from android_world.env import json_action
from android_world.task_evals.task_eval import TaskEval
from android_world.task_evals.information_retrieval.proto_utils import get_expected_answer

from evaluation.auto_test import AutoTest, Instance_AndroidWorld, Instance
from evaluation.evaluation import *
from evaluation.auto_test import find_package
from recorder import JSONRecorder

from evaluation.docker_utils import create_docker_container, execute_command_in_container, remove_docker_container, \
    start_avd, stop_avd
    
import docker
from docker.types import Mount

'''
def split_dict(input_dict, n = 1):
    if not isinstance(input_dict, dict) or not isinstance(n, int) or n <= 0:
        raise ValueError("输入参数不合法，input_dict 应为字典，n 应为正整数")
    
    items = list(input_dict.items())
    return [dict(items[i:i + n]) for i in range(0, len(items), n)]'''

def split_dict(input_dict, n=1):
    if not isinstance(input_dict, dict) or not isinstance(n, int) or n <= 0:
        raise ValueError("输入参数不合法，input_dict 应为字典，n 应为正整数")

    # 展开原始字典的值，使每个列表元素单独存放在一个长度为1的list中
    expanded_items = []
    for key, value in input_dict.items():
        if isinstance(value, list) and len(value) > 1:
            for v in value:
                expanded_items.append((key, [v]))  # 仍然存为 list，但长度为 1
        else:
            expanded_items.append((key, value if not isinstance(value, list) else [value[0]]))

    # 按照 n 进行切分
    return [dict(expanded_items[i:i + n]) for i in range(0, len(expanded_items), n)]

_TASKS = None
_FIXED_TASK_SEED = False
_TASK_RANDOM_SEED = 30
_N_TASK_COMBINATIONS = 1
_EMULATOR_SETUP = False
_SUITE_FAMILY = registry.TaskRegistry.ANDROID_WORLD_FAMILY
# other:registry.TaskRegistry.MINIWOB_FAMILY_SUBSET
  

def markor_fix(state, env, get_post_transition_state):
    x = None
    y = None
    for ui_element in state.ui_elements:
        print(ui_element.text)
        if ui_element.text == "OK":
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
    post_transition_state = get_post_transition_state()
    
    x = None
    y = None
    for ui_element in post_transition_state.ui_elements:
        if ui_element.class_name == "android.widget.Switch":
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
    post_transition_state = get_post_transition_state()
    for ui_element in post_transition_state.ui_elements:
        if ui_element.content_description == "Navigate up":
            bbox_pixels = ui_element.bbox_pixels
            x = (bbox_pixels.x_min + bbox_pixels.x_max) / 2
            y = (bbox_pixels.y_min + bbox_pixels.y_max) / 2
            break
    if x is not None and y is not None:
        action = json_action.JSONAction(**{'action_type':'click', 'x':x,'y':y})
        env.execute_action(action)
        time.sleep(2)
    post_transition_state = get_post_transition_state()
    
    return post_transition_state

def android_world_answer(state, env, finish_message):
    action = json_action.JSONAction(**{'action_type':'answer', 'text':finish_message})
    env.execute_action(action)


def print_android_world_results(path = None, all_results = None):
    df = process_episodes(all_results, print_summary = True)
    df.to_excel(os.path.join(path, "results.xlsx"), index=True)
    return df
     
def check_device_connected(device_port):
    time.sleep(2)
    try_time = 0
    while try_time <= 10:
        adb_connect_cmd = f"adb connect localhost:{device_port}"
        #print_with_color(f"Trying to connect to AVD via: {adb_connect_cmd}", "blue")
        connect_result = execute_adb(adb_connect_cmd, output=True)

        if "connected" not in connect_result and "already connected" not in connect_result:
            pass
            #print_with_color(f"ADB connect failed: {connect_result}", "red")
        else:
            break
        try_time += 1
        time.sleep(2)

    # 等待设备可用
    wait_cmd = f"adb -s localhost:{device_port} wait-for-device"
    print_with_color("Waiting for device to become available...", "blue")
    try:
        subprocess.run(wait_cmd.split(), timeout=120)
    except subprocess.TimeoutExpired:
        print_with_color("ADB wait-for-device timeout", "red")
        return False

    device = f"localhost:{device_port}"
    
    return device
        
class Instance_AndroidWorld_docker(Instance_AndroidWorld):
    def __init__(self, config, idx = 0, start_idx = 0):
        self.idx = str(idx+start_idx)+str(time.time())  
        self.type = "cmd"
        self.config = config
        self.container_id = None
        self.docker_port_local = None
        self.avd_name = None
        self.tar_avd_dir = None
        self.tar_ini_file = None
        device_start_port = self.config.device_start_port
        grpc_start_port = self.config.grpc_start_port
        idx_num = idx+start_idx
        self.device_port = device_start_port + idx_num * 4
        self.grpc_port = grpc_start_port + idx_num * 4


    def initialize_single_task(self, config=None):
        avd_name = self.avd_name
        print_with_color(f"Starting Android Emulator in Docker with AVD name: {avd_name}", "blue")

        client = docker.from_env()

        adbkey_path = os.path.expanduser("~/.android/adbkey")
        with open(adbkey_path, "r") as f:
            adbkey_content = f.read()

        port_1 = self.grpc_port     # 8554
        port_2 = self.device_port   # 5555

        try:
            container = client.containers.run(
                image="android_world:v2",
                detach=True,
                network_mode="host",
                environment={
                    "ADBKEY": adbkey_content
                },
                devices=["/dev/kvm"],
                name=f"android_emulator_{self.idx}",
                remove=True,
                stdout=True,
                stderr=True,
                volumes={
                    os.path.join(os.getcwd(), 'tmp'): {'bind': os.path.join(os.getcwd(), 'tmp'), 'mode': 'rw'}
                }
            )
            
            self.container_id = container.id
            print_with_color(f"Container started with ID: {self.container_id}", "green")
        except docker.errors.APIError as e:
            print_with_color(f"Failed to start container: {str(e)}", "red")
            return False

        device = f"emulator-{self.device_port-1}"

  
        '''
        print_with_color("Emulator in Docker started successfully", "blue")

        # 检查 boot 动画是否完成
        limit_time = time.time() + 120
        while True:
            boot_complete = f"adb -s {device} shell getprop init.svc.bootanim"
            boot_complete = execute_adb(boot_complete, output=False)
            if boot_complete == 'stopped':
                print_with_color("Emulator boot completed", "blue")
                break
            if time.time() > limit_time:
                print_with_color("Emulator boot timeout", "red")
                return False
            time.sleep(1)'''

        self.docker_container = container
        return device

    def stop_single_task(self):
        pass
        '''
        print_with_color("Stopping Docker Android Emulator...", "blue")
        try:
            if self.container_id:
                client = docker.from_env()
                container = client.containers.get(self.container_id)
                container.stop()
                print_with_color("Docker container stopped", "blue")
                time.sleep(2)
            else:
                assert False, "Container ID is not set"
        except Exception as e:
            print_with_color(f"Failed to stop container: {str(e)}", "red")'''

    def __del__(self):
        print_with_color("Stopping Docker Android Emulator...", "blue")
        try:
            if self.container_id:
                client = docker.from_env()
                container = client.containers.get(self.container_id)
                container.stop()
                print_with_color("Docker container stopped", "blue")
                time.sleep(2)
            else:
                assert False, "Container ID is not set"
        except Exception as e:
            print_with_color(f"Failed to stop container: {str(e)}", "red")
     
        
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
      transition_pause = 5.0,
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
    self.transition_pause = transition_pause

  def step(self, goal: str) -> base_agent.AgentInteractionResult:
    """See base class."""
    round_count = self.autotest_agent.record.get_round_count()
    
    if round_count == 0:
        print("launch app: ", find_package(self.app))
        self.controller.launch_app(find_package(self.app))
        time.sleep(5)
    state = self.get_post_transition_state()
    if round_count == 0 and not self.autotest_agent.controller.check_ac_survive():
        #turn_on_ac(state, self.env)
        command = 'adb shell settings put secure enabled_accessibility_services \
"$(adb shell settings get secure enabled_accessibility_services):com.google.androidenv.accessibilityforwarder/.AccessibilityForwarder:com.example.android.xml_parser/.XMLParserAccessibilityService"'
        self.controller.run_command(command)
        time.sleep(1)
        self.autotest_agent.accessibility = self.autotest_agent.controller.check_ac_survive()
    
    if find_package(self.app).strip() == "net.gsantner.markor" and round_count == 0:
        state = markor_fix(state, self.env, self.get_post_transition_state)

    self.autotest_agent.run_step()
    try:
        latest_action = self.autotest_agent.record.get_latest_parsed_action()
        if latest_action.get("operation") == 'finish':
            finish_message = latest_action.get("kwargs",{}).get("message", None)
            android_world_answer(state, self.env, finish_message)
    except:
        import traceback
        traceback.print_exc()
        done = True
    
    
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
    time.sleep(self.transition_pause)
    return base_agent.AgentInteractionResult(
        done,
        step_data,
    )

class Empty_Task(TaskEval):
  """Base class for Camera tasks."""

  app_names = ("camera",)
  complexity = 1
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "Take one photo."

  def _clear_app_data(self, env: interface.AsyncEnv) -> None:
    pass

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    pass

  def tear_down(self, env: interface.AsyncEnv):
    super().tear_down(env)
    self._clear_app_data(env)

    
  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}

def initialize_android_world_suite(task_template = None, n_task_combinations = 1, seed = 30):
    n_task_combinations = n_task_combinations
    task_registry = registry.TaskRegistry()
    suite = suite_utils.create_suite(
        task_registry.get_registry(family=_SUITE_FAMILY),
        n_task_combinations=n_task_combinations,
        seed=seed,
        tasks=task_template,
        use_identical_params=_FIXED_TASK_SEED,
    )
    suite.suite_family = _SUITE_FAMILY
    return suite

class AndroidWorld_AutoTest(AutoTest):
    def __init__(self, config, base_class, llm_agent, docker_idx = 0, parallel_start_num = 0) -> None:
        self.config = config
        self.base_class = base_class
        self.llm_agent = llm_agent
        self.docker_idx = docker_idx
        self.parallel_start_num = parallel_start_num
        self.instance = Instance_AndroidWorld_docker(self.config, self.docker_idx, self.parallel_start_num)
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
        env = load_and_setup_env(
            console_port=instance.device_port,
            emulator_setup=_EMULATOR_SETUP,
            adb_path=f'docker exec {instance.container_id} /android/sdk/platform-tools/adb',
            grpc_port=instance.grpc_port
        )

        self.env = env

        self.controller = AndroidController(device, type, instance)


    def run_serial(self, tasks):
        instance = Instance_AndroidWorld_docker(self.config)
        for task in tasks:
            self.run_task(task, instance)

    def run_task(self, suite, instance = None):
        if instance is None:
            instance = self.instance
        task_id = list(suite.keys())[0]
        app = suite[task_id][0].app_names[-1]
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

        self.env.close()
        instance.stop_single_task()

        with jsonlines.open(os.path.join(self.config.task_dir, "results.jsonl"), "w") as writer:
            for result in results:
                writer.write(result)

        return results

    def get_agent(self):
        return self.base_class.get_agent()

    def get_executor(self):
        return self.base_class.get_executor()


class AndroidWorld_Sample(AndroidWorld_AutoTest):
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
        self.controller = AndroidController(device, type, instance)


    def run_serial(self, tasks):
        for task in tasks:
            self.android_world_task_wrapper(task)

    def android_world_task_wrapper(self, task, instance = None):
        if instance is None:
            instance = Instance_AndroidWorld_test(self.config)
        instance.initialize_single_task(self.config)
        adb_path = self.config.adb_path
        env = env_launcher.load_and_setup_env(
            console_port=instance.device_port,
            emulator_setup=_EMULATOR_SETUP,
            adb_path=adb_path,
            grpc_port=instance.grpc_port
        )

        self.env = env

        if task["suite"] is not None:
            for key, value in task["suite"].items():
                task_eval = value[0]
        else:
            task_eval = Empty_Task(params={})

        if task["suite"] is not None:
            task_eval.initialize_task(self.env)
        self.run_task(task, instance)
        task_eval.tear_down(self.env)
        return None
 
    def run_task(self, suite, instance):
        self.base_class.run_task(suite, instance)

    def get_agent(self):
        return self.base_class.get_agent()

    def get_executor(self):
        return self.base_class.get_executor()

    def get_executor(self):
        return self.base_class.get_executor()
