import json
import jsonlines
import glob
import os
import random
# import itertools
import re
import base64
import unicodedata
import traceback
from collections import defaultdict

from tqdm import tqdm
from PIL import Image
from reward_worker.generate_combined_image import merge_single_task
from agent.mllm.qwen_model import Qwen2VLAgent_reward
from reward_worker.utils import (
    build_android_prompt_gpt_with_image,
    build_android_prompt_gpt_with_xml,
    extract_content,
    get_glm_completion,
    image_to_base64
)
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
#from transformers import AutoTokenizer



apps_dict = {
    "桌面": "com.google.android.apps.nexuslauncher",
    "Spotify": "com.spotify.music",
    "Contacts": "com.google.android.contacts",
    "Settings": "com.android.settings",
    "Setting": "com.android.settings",
    "Android-System-Setting": "com.android.settings",
    "设置": "com.android.settings",
    "Clock": "com.google.android.deskclock",
    "TikTok": "com.zhiliaoapp.musically",
    "Clash": "com.github.kr328.clash",
    "Amazon Shopping": "com.amazon.mShop.android.shopping",
    "AmazonShopping": "com.amazon.mShop.android.shopping",
    "Snapchat": "com.snapchat.android",
    "Slack": "com.Slack",
    "Uber": "com.ubercab",
    "Reddit": "com.reddit.frontpage",
    "Twitter": "com.twitter.android",
    "X": "com.twitter.android",
    "Quora": "com.quora.android",
    "Zoom": "us.zoom.videomeetings",
    "Booking": "com.booking",
    "Instagram": "com.instagram.android",
    "Facebook": "com.facebook.katana",
    "WhatsApp": "com.whatsapp",
    "Google_Maps": "com.google.android.apps.maps",
    "GoogleMap": "com.google.android.apps.maps",
    "YouTube": "com.google.android.youtube",
    "Netflix": "com.netflix.mediaclient",
    "LinkedIn": "com.linkedin.android",
    "Google Drive": "com.google.android.apps.docs",
    "GoogleDrive": "com.google.android.apps.docs",
    "Gmail": "com.google.android.gm",
    "Chrome": "com.android.chrome",
    "Twitch": "tv.twitch.android.app",
    "Wechat": "com.tencent.mm",
    "微信": "com.tencent.mm",
    "高德地图": "com.autonavi.minimap",
    "高德": "com.autonavi.minimap",
    "美团": "com.sankuai.meituan",
    "meituan": "com.sankuai.meituan",
    "Calendar": "com.skuld.calendario",
    "weather": "org.breezyweather",
    "Map.me": "com.mapswithme.maps.pro",
    "Map": "com.mapswithme.maps.pro",
    "bleucoins": "com.rammigsoftware.bluecoins",
    "Cantook": "com.aldiko.android",
    "PiMusicPlayer": "com.Project100Pi.themusicplayer",
    "Firefox": "org.mozilla.firefox",
    "simple_notepad": "org.mightyfrog.android.simplenotepad",
    "tasks": "com.tarento.tasks",
    "vlc": "org.videolan.vlc",
    "PlayStore": "com.android.vending",
}

from Levenshtein import distance




def find_closest(input_str, dict):
    if input_str in dict:
        return dict[input_str]
    elif input_str.replace(" ", "").lower() in dict:
        return dict[input_str.replace(" ", "").lower()]

    input_str = input_str.replace(" ", "").lower()
    # 初始化变量来追踪最小编辑距离及其对应的key
    min_distance = float('inf')
    closest_key = None

    # 遍历字典中的所有key，找到与输入字符串编辑距离最小的key
    for key in dict:
        origin_key = key
        key = key.replace(" ", "").lower()
        current_distance = distance(input_str, key)
        if current_distance < min_distance:
            min_distance = current_distance
            closest_key = origin_key

    # 返回编辑距离最小的key的value
    return dict[closest_key]

def find_app(input_str: str) -> str:
    inverse_dict = {v: k for k, v in apps_dict.items()}
    return find_closest(input_str, inverse_dict)

train_docs, train_action_only_docs = [], []
#tokenizer = AutoTokenizer.from_pretrained('/raid/xuyifan/checkpoint/meta-llama-3.1-8b-instruct')
stats = defaultdict(int)
extra_long_files = set()


class Trace:
    def __init__(self, path, docs, add_combined_reward_model=False, combined_pic_path=None,reward_model_type=None):
        self.log_path = path
        self.raw_turns = docs
        self.formatted_history = []
        self.add_combined_reward_model = add_combined_reward_model
        self.combined_pic_path = combined_pic_path
        self.reward_model_type = reward_model_type

    def get_code_snippet(self, content):
        if len(content.split('\n')) == 1:
            return content
        code = re.search(r'```[\s\S]*?\n([\s\S]+?)\n```', content)
        if code is None:
            print(f"Extracting code from {content} failed. Return response directly.")
            return content
            # raise RuntimeError()
        code = code.group(1)
        return code
    
    def prompt_to_message(self, prompt, images, system_msg):
        content = [{"type": "text", "text": prompt}]
        for img in images:
            base64_img = image_to_base64(img)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"},
                }
            )

        message = []
        if system_msg is not None:
            message.append({"role": "system", "content": system_msg})
        message.append({"role": "user", "content": content})
        return message
    
    def add_combined_reward(self, log_path, res):
        final_image_path = merge_single_task(log_path, self.combined_pic_path)
        instruction = res["instruction"]
        response = res["response"]
        format_operation = res["format_hostory_list"][:-1]
        history = "\n".join(
            [f"{idx + 1}: {action}" for idx, action in enumerate(format_operation)]
        )
        prompt, system_msg = build_android_prompt_gpt_with_image(
            instruction, response, history
        )
        images_path = final_image_path
        reward_message = self.prompt_to_message(prompt, [images_path], system_msg)
        return reward_message, final_image_path


    def format_single_action_only_sample(self, index, turns):
        turn = turns[index]
        # extracted_code = self.get_code_snippet(turn['response'])
        # assert extracted_code == turn['code']

        instruction = turn['target']
        current_compressed_xml_path = os.path.join(self.log_path, 'xml', f'{index}_compressed_xml.txt')
        with open(current_compressed_xml_path, 'r', encoding='utf-8') as f:
            current_compressed_xml = f.read()

        current_image_path = None

        history = ""
        formatted_history = []
        for i in range(index - 1, -1, -1):
            #observation = f"\n\n<|observation|>\n{turns[i]['observation']}" if turns[i].get('observation') else ""
            #note = self.format_note(turns[i])
            prompt = turns[i]['target'] if i == 0 else "** XML **"
            history = f"Round {i}\n\n<|user|>\n{prompt}\n\n<|assistant|>\n{turns[i]['current_response']}\n\n" + history
            formatted_history.append(turns[i]['current_response'])

        app = find_app(turn['current_activity'])

        status = json.dumps({"current_app": app}, ensure_ascii=False)
        prompt = turns[index]['target'] if index == 0 else "** XML **"
        current_turn = f"Round {index}\n\n<|user|>\n{prompt}\n\n{status}\n{current_compressed_xml}\n\n<|assistant|>\n"

        res = {
            "uid": f"{self.log_path}_{index}",
            "app": app,
            "current_activity": turn['current_activity'],
            "instruction": instruction,
            "format_hostory_list": formatted_history,
            "history": history.replace("\n<|user|>", "<|user|>:").replace("\n<|assistant|>", "<|assistant|>:"),
            "parsed_action": turn['parsed_action'],
            "original_action": turn.get('original_action'),
            "image": current_image_path,
            "source": self.log_path,
            "prompt": f"{history}{current_turn}",
            "response": turn['current_response']  # self.get_code_snippet(turn['response'])
        }

        if self.add_combined_reward_model:
            assert self.reward_model_type == "combined_image_qwen", "Only support combined_image_qwen now"
            if turn['parsed_action']["operation"] == "finish":
                reward_message, final_image_path = self.add_combined_reward(self.log_path, res)
                res["reward_model_type"] = self.reward_model_type
                res["final_combined_image"] = final_image_path
                res["reward_message"] = reward_message

        

        return res
    
class ActionProcessor:
    def __init__(self):
        self.train_action_only_docs = []

    def processor_action_only(self, trace, index, turns):
        doc = trace.format_single_action_only_sample(index, turns)
        self.train_action_only_docs.append(doc)
    
def process_reward(agent, line):
    """处理单个 JSONL 行的逻辑"""
    message = line.pop("reward_message")
    response = agent.act(message)
    thoughts = extract_content(response, "Thoughts:")
    status = extract_content(response, "Status:")
    line["thoughts"] = thoughts
    line["status"] = status
    line["reward"] = 1 if "YES" in status else 0
    return line

def format_sample(base_folder_path=None, save_folder_path=None, add_combined_reward_model=True, reward_model_type="combined_image_qwen", save_combined_pic_path=None):
    
    if add_combined_reward_model and save_combined_pic_path is None:
        save_combined_pic_path = f"{save_folder_path}/combined"

    os.makedirs(save_folder_path, exist_ok=True)
    version_stats_out = open(f"{save_folder_path}/VERSION", "w")

    random.seed(34)
    futures = []
    processor = ActionProcessor()
    with ThreadPoolExecutor(64) as pool:
        for hyper_dir in [f'{base_folder_path}/{d}' for d in os.listdir(f'{base_folder_path}')]: 
            print("Processing", hyper_dir)
            version_stats_out.write(hyper_dir + '\n')
            assert os.path.exists(f'{hyper_dir}')
            for directory in tqdm(glob.glob(f'{hyper_dir}/*')):
                #print(directory)
                file = f"{directory}/traces/trace.jsonl"
                if not os.path.exists(file):
                    continue
                with jsonlines.open(file, 'r') as f:
                    turns = list(f)
                trace = Trace(directory, docs=turns, add_combined_reward_model=add_combined_reward_model, combined_pic_path=save_combined_pic_path, reward_model_type=reward_model_type)
                for index in range(len(turns)):
                    futures.append(pool.submit(processor.processor_action_only, trace, index, turns))
        wait(futures)
    json.dump(list(extra_long_files), open(f"{save_folder_path}/EXTRA_LONG_FILES.json", "w"), indent=4, ensure_ascii=False)
    print("Train:", len(processor.train_action_only_docs))
    #stats = sorted(stats.items(), key=lambda x: x[0], reverse=True)
    #stats = [(f"{key}-{key + 1000}", value) for key, value in stats]
    #print(stats)

    if add_combined_reward_model:
        with jsonlines.open(f"{save_folder_path}/train_action_only.jsonl", "w") as f,jsonlines.open(f"{save_folder_path}/final_combined_messages.jsonl", "w") as f2:
            for doc in processor.train_action_only_docs:
                if doc['parsed_action']["operation"] == "finish":
                    f2.write(doc)
                    del doc["final_combined_image"]
                    del doc["reward_message"]
                    del doc["reward_model_type"]
                f.write(doc)
        
    else:
        with jsonlines.open(f"{save_folder_path}/train_action_only.jsonl", "w") as f:
            for doc in processor.train_action_only_docs:
                f.write(doc)

    '''

    if add_combined_reward_model:
        agent = Qwen2VLAgent(model_name="Qwen2-VL-7B-Instruct-Reward", url="http://10.32.0.102:10013/v1/chat/completions")
        input_file = f"{save_folder_path}/final_combined_messages.jsonl"
        output_file = f"{save_folder_path}/final_combined_messages_reward.jsonl"
        with jsonlines.open(input_file) as f, jsonlines.open(output_file, "w") as f2:
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = {executor.submit(process_reward, agent, line): line for line in f}
                for future in tqdm(as_completed(futures), total=len(futures)):
                    processed_line = future.result()
                    f2.write(processed_line)'''
    version_stats_out.close()
    
    # to digirl format
    reward_dict = {}
    if add_combined_reward_model:
        with jsonlines.open(f"{save_folder_path}/final_combined_messages_reward.jsonl") as f:
            for line in f:
                reward_dict[line["source"]] = line["reward"]

    task_dict = defaultdict(list)
    with jsonlines.open(f"{save_folder_path}/train_action_only.jsonl") as f:
        for line in f:
            idx = int(line["uid"].split("_")[-1])
            task_dict[line["source"]].append({"idx": idx, "line": line})
        train_docs = []
    for _, lines in task_dict.items():
        lines.sort(key=lambda x: x["idx"])
        output_lines = []
        for i in range(len(lines)):
            line = lines[i]
            if i == len(lines) - 1:
                next_observation = line["line"]["prompt"]
                done = True
            else:
                next_line = lines[i + 1]
                next_observation = next_line["line"]["prompt"]
                done = False
            line = line["line"]
    
            item = {
                "trace_id": line["source"],
                "step_id": line["uid"],
                "observation": line["prompt"],
                "action": line["response"],
                "reward": reward_dict.get(line["source"], 0),
                "next_observation": next_observation,
                "done": done,
                "trajectory_reward": reward_dict.get(line["source"], 0),
                "task": line["instruction"],
                "mc_return": 0,
            }
            output_lines.append(item)
        train_docs.append(output_lines)
    with jsonlines.open(f"{save_folder_path}/digirl-format.jsonl", "w") as f:
        for doc in train_docs:
            f.write(doc)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_folder_path', type=str, default='/raid/xuyifan/Android-Lab-main/sample_test')
    parser.add_argument('--save_folder_path', type=str, default='/raid/xuyifan/Android-Lab-main/sample_test-format')
    parser.add_argument('--add_combined_reward_model', action='store_true')
    parser.add_argument('--reward_model_type', default='combined_image_qwen')
    parser.add_argument('--save_combined_pic_path', type=str, default='/raid/xuyifan/Android-Lab-main/sample_test-format/combined')
    args = parser.parse_args()
    format_sample(args.base_folder_path, args.save_folder_path, args.add_combined_reward_model, args.reward_model_type, args.save_combined_pic_path)
