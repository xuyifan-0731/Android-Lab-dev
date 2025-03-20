import re
import json
import time
from PIL import Image
from transformers import PreTrainedTokenizerFast

from agent.model import *
import base64
from templates.android_screenshot_template import SYSTEM_PROMPT_ANDROID_MLLM_CogAgent

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def format_bbox(bbox, window):
    # For x1, y1, x2, y2 format bbox
    x1 = min(int(bbox[0] / window[0] * 1000), 999)
    y1 = min(int(bbox[1] / window[1] * 1000), 999)
    x2 = min(int(bbox[2] / window[0] * 1000), 999)
    y2 = min(int(bbox[3] / window[1] * 1000), 999)
    return f"[{x1:03d},{y1:03d},{x2:03d},{y2:03d}]"


def remove_leading_zeros_in_string(s):
    # 使用正则表达式匹配列表中的每个数值并去除前导零
    return re.sub(r'\b0+(\d)', r'\1', s)


def format_response(content, window_size):
    # 1. Check if linebreak in response
    if len(content.split('\n')) > 1:
        # print(f"Response `{content}` is not a valid code. Replace all `\\n` with `\\\\n`.")
        content = content.replace('\n', '\\n')

    # 2. Check if element exists and replace to relative bbox
    element = re.search(r"element=(\[\d+,\d+,\d+,\d+\])", content)
    if element is not None:
        absolute_bbox = eval(remove_leading_zeros_in_string(element.group(1)))
        relative_bbox = format_bbox(absolute_bbox, window_size)
        content = content.replace(element.group(0), f"element={relative_bbox}")

    return content


class CogagentAgent(OpenAIAgent):
    def __init__(
            self,
            url: str,
            model_name: str = "",
            max_new_tokens: int = 512,
            temperature: float = 0,
            top_p: float = 0.7,
            **kwargs
    ) -> None:
        self.url = url
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.kwargs = kwargs
        self.name = model_name
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained(
            "/raid/xuyifan/pipeline-sample/pipeline-mobile/agent/model/Meta-Llama-3-8B-Instruct")

    @backoff.on_exception(
        backoff.expo, Exception,
        on_backoff=handle_backoff,
        on_giveup=handle_giveup,
        max_tries=10
    )
    def act(self, messages: List[Dict[str, Any]]) -> str:
        proxy = {
            'http': 'socks5h://127.0.0.1:8889',
            'https': 'socks5h://127.0.0.1:8889'
        }
        messages = self.format_message(messages)
        # print(messages)
        try:
            response = requests.post(self.url, files=messages[0], data=messages[1], timeout=480,
                                     proxies=proxy)
            print(response.text)
            response = response.json()
        except Exception as e:
            import traceback
            traceback.print_exc()
            return str(e)

        if "error" in response:
            return response["error"]["message"]
        response["response"] = response["response"].split("<|end_of_text|>")[0]
        return response["response"]

    def system_prompt(self, instruction) -> str:
        return SYSTEM_PROMPT_ANDROID_MLLM_CogAgent + f"\n\nTask Instruction: {instruction}"

    def prompt_to_message(self, prompt, images):
        content = [{
            "type": "text",
            "text": prompt
        }]
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img}",
                    "detail": "high"
                }
            })
        message = {
            "role": "user",
            "content": content
        }
        return message

    def format_message(self, messages):
        # TODO: support note and observation
        history = []

        messages = replace_image_url(messages, throw_details=True, keep_path=True)
        images = []
        for message in messages:
            if message["role"] == "user":
                if isinstance(message["content"], str):
                    continue
                for content in message["content"]:
                    if content.get("image_url"):
                        images.append(content["image_url"]["url"].split("file://")[-1])
        window_size = Image.open(images[0]).size
        images = [open(image, "rb") for image in images]

        system_prompt = messages[0]["content"]
        index = len([message for message in messages if message["role"] == "user"]) - 1
        status = messages[-1]["content"][0]["text"] if index > 0 else "{}"
        current_turn = f"Round {index}\n\n<|user|>\n{status}\n\n<|assistant|>\n"
        for i in range(index - 1, -1, -1):
            turn = messages[i * 2 + 2]
            text = turn["content"] if isinstance(turn["content"], str) else turn["content"][0]["text"]
            text = format_response(text, window_size)
            processed_turn_text = f"Round {i}\n\n<|user|>\n** SCREENSHOT **\n\n<|assistant|>\n{text}"
            length = len(self.tokenizer.tokenize(
                "\n\n".join([system_prompt,
                             "** Earlier trajectory has been truncated **", processed_turn_text] + history + [
                                current_turn])))
            if (length > 8192 - 2304 - 50 - 512):
                history = ["** Earlier trajectory has been truncated **"] + history
                # print(f"Task {self.task_id} truncated at turn {index} due to length ({length}).")
                break
            else:
                history = [processed_turn_text] + history
        history = [f"<|system|>\n{system_prompt}"] + history
        history.append(current_turn)
        prompt = "\n\n".join(history)

        new_messages = [
            {"image": images[0]},
            {"prompt": prompt}
        ]
        return new_messages
    

class CogagentAgent_09(CogagentAgent):
    # for swift deploy model(vab)
    def format_message(self, messages):
        # TODO: support note and observation
        history = []

        #messages = replace_image_url(messages, throw_details=True, keep_path=True)
        images = []
        for message in messages:
            if message["role"] == "user":
                if isinstance(message["content"], str):
                    continue
                for content in message["content"]:
                    if content.get("image_url"):
                        images.append(content["image_url"]["url"].split("data:image/png;base64,")[-1])
        window_size = Image.open(images[0]).size
        images = [open(image, "rb") for image in images]
        system_prompt = messages[0]["content"]
        instruction = system_prompt.split("Task Instruction: ")[-1]
        
        index = len([message for message in messages if message["role"] == "user"]) - 1
        status = messages[-1]["content"][0]["text"] if index > 0 else "{}"

        if index == 0:
            current_turn = f"Round {index}\n\n<|user|>{instruction}\n\n{status}<|assistant|>\n"
        else:
            current_turn = f"Round {index}\n\n<|user|>** SCREENSHOT **\n\n{status}<|assistant|>\n"
        for i in range(index - 1, -1, -1):
            turn = messages[i * 2 + 2]
            text = turn["content"] if isinstance(turn["content"], str) else turn["content"][0]["text"]
            #text = format_response(text, window_size)
            if i == 0:
                processed_turn_text = f"Round {i}\n\n<|user|>{instruction}<|assistant|>\n{text}"
            else:
                processed_turn_text = f"Round {i}\n\n<|user|>** SCREENSHOT **<|assistant|>\n{text}"
            length = len(self.tokenizer.tokenize(
                "\n\n".join([system_prompt,
                             "** Earlier trajectory has been truncated **", processed_turn_text] + history + [
                                current_turn])))
            if (length > 8192 - 2304 - 50 - 512):
                history = ["** Earlier trajectory has been truncated **"] + history
                # print(f"Task {self.task_id} truncated at turn {index} due to length ({length}).")
                break
            else:
                history = [processed_turn_text] + history
        history.append(current_turn)
        prompt = "\n\n".join(history)

        new_messages = [
            {"image": images[0]},
            {"prompt": prompt}
        ]

        # print(new_messages)

        return new_messages


    
class Qwen2VLAgent(CogagentAgent):
    @backoff.on_exception(
    backoff.expo, Exception,
    on_backoff=handle_backoff,
    on_giveup=handle_giveup,
    max_tries=10
    )
    def act(self, messages: List[Dict[str, Any]]) -> str:
        messages = self.format_message(messages)
        proxy = {
        'http': 'socks5h://127.0.0.1:8889',
        'https': 'socks5h://127.0.0.1:8889'
        }
        headers = {
            'Content-Type': 'application/json',
            # 'Host': ''
        }
        data = {
            'model': self.name,
            #'model': "Llama-3.2-11B-Vision-Instruct",
            'messages': messages,
            #'seed': 34,
            'temperature': self.temperature,
            #'stream': False
        }
        response = requests.post(self.url, headers=headers, json=data, proxies=proxy)
        #print(response)
        if response.status_code != 200:
            print(response.text)

        return response.json()["choices"][0]["message"]["content"]

    def prompt_to_message(self, prompt, images):
        content = [{
            "type": "text",
            "text": prompt
        }]

        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"{img}",
                }
            })
        message = {
            "role": "user",
            "content": content
        }
        return message
    
    def format_message(self, messages):
        # TODO: support note and observation
        history = []
        images = []
        
        for message in messages:
            if message["role"] == "user":
                if isinstance(message["content"], str):
                    continue
                for content in message["content"]:
                    if content.get("image_url"):
                        images.append(content["image_url"]["url"])
        #window_size = Image.open(images[0]).size
        #images = [open(image, "rb") for image in images]
        system_prompt = "<image>"
        instruction = messages[0]["content"].replace("<image>","")
        index = len([message for message in messages if message["role"] == "user"]) - 1
        status = messages[-1]["content"][0]["text"] if index > 0 else "{}"
        if index == 0:
            current_turn = f"Round {index}\n\n<|user|>{instruction}\n\n{status}<|assistant|>\n"
        else:
            current_turn = f"Round {index}\n\n<|user|>** SCREENSHOT **\n\n{status}<|assistant|>\n"
        for i in range(index - 1, -1, -1):
            turn = messages[i * 2 + 2]
            text = turn["content"] if isinstance(turn["content"], str) else turn["content"][0]["text"]
            #text = format_response(text, window_size)
            if i == 0:
                processed_turn_text = f"Round {i}\n\n<|user|>{instruction}<|assistant|>\n{text}"
            else:
                processed_turn_text = f"Round {i}\n\n<|user|>** SCREENSHOT **<|assistant|>\n{text}"
            length = len(self.tokenizer.tokenize(
                "\n\n".join([system_prompt,
                             "** Earlier trajectory has been truncated **", processed_turn_text] + history + [
                                current_turn])))
            if (length > 8192 - 2304 - 50 - 512):
                history = ["** Earlier trajectory has been truncated **"] + history
                # print(f"Task {self.task_id} truncated at turn {index} due to length ({length}).")
                break
            else:
                history = [processed_turn_text] + history
        history.append(current_turn)
        prompt = "\n\n".join(history).lstrip("\n")
        prompt = system_prompt + prompt
        path_to_image = images[0]
        with open(path_to_image, "rb") as f:
            encoded_image = base64.b64encode(f.read())
        encoded_image_text = encoded_image.decode("utf-8")
        base64_qwen = f"data:image;base64,{encoded_image_text}"

        content = [{
                    "type": "image_url",
                    "image_url": {
                        "url": base64_qwen
                    },
                },
                {"type": "text", "text": prompt},]
        new_messages = [{
                "role": "user",
                "content": content
        }]

        return new_messages

class Qwen2VLAgent_full_prompt(Qwen2VLAgent):
    def format_message(self, messages):
        # TODO: support note and observation
        history = []
        images = []
        
        for message in messages:
            if message["role"] == "user":
                if isinstance(message["content"], str):
                    continue
                for content in message["content"]:
                    if content.get("image_url"):
                        images.append(content["image_url"]["url"])
        #window_size = Image.open(images[0]).size
        #images = [open(image, "rb") for image in images]
        instruction = messages[0]["content"].replace("<image>","")
        system_prompt = "<image><|system|>\n" + self.system_prompt(instruction) + "\n\n"
        
        index = len([message for message in messages if message["role"] == "user"]) - 1
        status = messages[-1]["content"][0]["text"] if index > 0 else "{}"
        if index == 0:
            current_turn = f"Round {index}\n\n<|user|>{instruction}\n\n{status}<|assistant|>\n"
        else:
            current_turn = f"Round {index}\n\n<|user|>** SCREENSHOT **\n\n{status}<|assistant|>\n"
        for i in range(index - 1, -1, -1):
            turn = messages[i * 2 + 2]
            text = turn["content"] if isinstance(turn["content"], str) else turn["content"][0]["text"]
            #text = format_response(text, window_size)
            if i == 0:
                processed_turn_text = f"Round {i}\n\n<|user|>{instruction}<|assistant|>\n{text}"
            else:
                processed_turn_text = f"Round {i}\n\n<|user|>** SCREENSHOT **<|assistant|>\n{text}"
            length = len(self.tokenizer.tokenize(
                "\n\n".join([system_prompt,
                             "** Earlier trajectory has been truncated **", processed_turn_text] + history + [
                                current_turn])))
            if (length > 8192 - 2304 - 50 - 512):
                history = ["** Earlier trajectory has been truncated **"] + history
                # print(f"Task {self.task_id} truncated at turn {index} due to length ({length}).")
                break
            else:
                history = [processed_turn_text] + history
        history.append(current_turn)
        prompt = "\n\n".join(history).lstrip("\n")
        prompt = system_prompt + prompt
        path_to_image = images[0]
        with open(path_to_image, "rb") as f:
            encoded_image = base64.b64encode(f.read())
        encoded_image_text = encoded_image.decode("utf-8")
        base64_qwen = f"data:image;base64,{encoded_image_text}"


        content = [{
                    "type": "image_url",
                    "image_url": {
                        "url": base64_qwen
                    },
                },
                {"type": "text", "text": prompt},]
        new_messages = [{
                "role": "user",
                "content": content
        }]

        return new_messages

class Llama_32_agent(Qwen2VLAgent):
    def format_message(self, messages):
        # TODO: support note and observation
        history = []
        images = []
        
        for message in messages:
            if message["role"] == "user":
                if isinstance(message["content"], str):
                    continue
                for content in message["content"]:
                    if content.get("image_url"):
                        images.append(content["image_url"]["url"])
        #window_size = Image.open(images[0]).size
        #images = [open(image, "rb") for image in images]
        system_prompt = ""
        instruction = messages[0]["content"].replace("<image>","")
        index = len([message for message in messages if message["role"] == "user"]) - 1
        status = messages[-1]["content"][0]["text"] if index > 0 else "{}"
        if index == 0:
            current_turn = f"Round {index}\n\n<|user|>{instruction}\n\n{status}<|assistant|>\n"
        else:
            current_turn = f"Round {index}\n\n<|user|>** SCREENSHOT **\n\n{status}<|assistant|>\n"
        for i in range(index - 1, -1, -1):
            turn = messages[i * 2 + 2]
            text = turn["content"] if isinstance(turn["content"], str) else turn["content"][0]["text"]
            #text = format_response(text, window_size)
            if i == 0:
                processed_turn_text = f"Round {i}\n\n<|user|>{instruction}<|assistant|>\n{text}"
            else:
                processed_turn_text = f"Round {i}\n\n<|user|>** SCREENSHOT **<|assistant|>\n{text}"
            length = len(self.tokenizer.tokenize(
                "\n\n".join([system_prompt,
                             "** Earlier trajectory has been truncated **", processed_turn_text] + history + [
                                current_turn])))
            if (length > 8192 - 2304 - 50 - 512):
                history = ["** Earlier trajectory has been truncated **"] + history
                # print(f"Task {self.task_id} truncated at turn {index} due to length ({length}).")
                break
            else:
                history = [processed_turn_text] + history
        history.append(current_turn)
        prompt = "\n\n".join(history).lstrip("\n")
        prompt = system_prompt + prompt
        path_to_image = images[0]
        with open(path_to_image, "rb") as f:
            encoded_image = base64.b64encode(f.read())
        encoded_image_text = encoded_image.decode("utf-8")
        base64_qwen = f"data:image/jpeg;base64,{encoded_image_text}"

        content = [{
                    "type": "image_url",
                    "image_url": {
                        "url": base64_qwen
                    },
                },
                {"type": "text", "text": prompt},]
        new_messages = [{
                "role": "user",
                "content": content
        }]

        return new_messages

class Glm4v_vllm_agent(Llama_32_agent):
    def format_message(self, messages):
        # TODO: support note and observation
        history = []
        images = []
        
        for message in messages:
            if message["role"] == "user":
                if isinstance(message["content"], str):
                    continue
                for content in message["content"]:
                    if content.get("image_url"):
                        images.append(content["image_url"]["url"])
        #window_size = Image.open(images[0]).size
        #images = [open(image, "rb") for image in images]
        system_prompt = ""
        instruction = messages[0]["content"].replace("<image>","")
        index = len([message for message in messages if message["role"] == "user"]) - 1
        status = messages[-1]["content"][0]["text"] if index > 0 else "{}"
        if index == 0:
            current_turn = f"Round {index}\n\n<|user|>{instruction}\n\n{status}<|assistant|>\n"
        else:
            current_turn = f"Round {index}\n\n<|user|>** SCREENSHOT **\n\n{status}<|assistant|>\n"
        for i in range(index - 1, -1, -1):
            turn = messages[i * 2 + 2]
            text = turn["content"] if isinstance(turn["content"], str) else turn["content"][0]["text"]
            #text = format_response(text, window_size)
            if i == 0:
                processed_turn_text = f"Round {i}\n\n<|user|>{instruction}<|assistant|>\n{text}"
            else:
                processed_turn_text = f"Round {i}\n\n<|user|>** SCREENSHOT **<|assistant|>\n{text}"
            length = len(self.tokenizer.tokenize(
                "\n\n".join([system_prompt,
                             "** Earlier trajectory has been truncated **", processed_turn_text] + history + [
                                current_turn])))
            if (length > 8192 - 2304 - 50 - 512):
                history = ["** Earlier trajectory has been truncated **"] + history
                # print(f"Task {self.task_id} truncated at turn {index} due to length ({length}).")
                break
            else:
                history = [processed_turn_text] + history
        history.append(current_turn)
        prompt = "\n\n".join(history).lstrip("\n")
        prompt = system_prompt + prompt
        path_to_image = images[0]
        with open(path_to_image, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode('utf-8')
        base64_images = [encoded_image]
        multi_modal_content = []
        multi_modal_prefix = ""

        # 根据图像数量生成对应的前缀
        multi_modal_prefix += "<|begin_of_image|><|endoftext|><|end_of_image|>" * len(base64_images)
        multi_modal_content += [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}",
                },
            } for image_base64 in base64_images
        ]

        # 构建对话内容
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": multi_modal_prefix + prompt}] + multi_modal_content
            }
        ]

        return messages

    @backoff.on_exception(
    backoff.expo, Exception,
    on_backoff=handle_backoff,
    on_giveup=handle_giveup,
    max_tries=10
    )
    def act(self, messages: List[Dict[str, Any]]) -> str:
        messages = self.format_message(messages)
        proxy = {
        'http': 'socks5h://127.0.0.1:8889',
        'https': 'socks5h://127.0.0.1:8889'
        }
        gen_kwargs = {
            "temperature": 0.001,
            "max_tokens": 512
        }
        payload = {
            "model": self.name,  # 替换为实际模型名称
            "messages": messages,
            "stream": False,
            **gen_kwargs
        }
        headers = {
            "Authorization": f"Bearer EMPTY",
            "Content-Type": "application/json"
        }

        response = requests.post(self.url, json=payload, headers=headers,proxies=proxy)
        #print(response)
        if response.status_code != 200:
            print(response.text)

        return response.json()["choices"][0]["message"]["content"]

class Llama_32_agent_full_prompt(Qwen2VLAgent_full_prompt):
    def format_message(self, messages):
        # TODO: support note and observation
        history = []
        images = []
        
        for message in messages:
            if message["role"] == "user":
                if isinstance(message["content"], str):
                    continue
                for content in message["content"]:
                    if content.get("image_url"):
                        images.append(content["image_url"]["url"])
        #window_size = Image.open(images[0]).size
        #images = [open(image, "rb") for image in images]
        instruction = messages[0]["content"].replace("<image>","")
        system_prompt = "<|system|>\n" + self.system_prompt(instruction) + "\n\n"
        
        index = len([message for message in messages if message["role"] == "user"]) - 1
        status = messages[-1]["content"][0]["text"] if index > 0 else "{}"
        if index == 0:
            current_turn = f"Round {index}\n\n<|user|>{instruction}\n\n{status}<|assistant|>\n"
        else:
            current_turn = f"Round {index}\n\n<|user|>** SCREENSHOT **\n\n{status}<|assistant|>\n"
        for i in range(index - 1, -1, -1):
            turn = messages[i * 2 + 2]
            text = turn["content"] if isinstance(turn["content"], str) else turn["content"][0]["text"]
            #text = format_response(text, window_size)
            if i == 0:
                processed_turn_text = f"Round {i}\n\n<|user|>{instruction}<|assistant|>\n{text}"
            else:
                processed_turn_text = f"Round {i}\n\n<|user|>** SCREENSHOT **<|assistant|>\n{text}"
            length = len(self.tokenizer.tokenize(
                "\n\n".join([system_prompt,
                             "** Earlier trajectory has been truncated **", processed_turn_text] + history + [
                                current_turn])))
            if (length > 8192 - 2304 - 50 - 512):
                history = ["** Earlier trajectory has been truncated **"] + history
                # print(f"Task {self.task_id} truncated at turn {index} due to length ({length}).")
                break
            else:
                history = [processed_turn_text] + history
        history.append(current_turn)
        prompt = "\n\n".join(history).lstrip("\n")
        prompt = system_prompt + prompt
        path_to_image = images[0]
        with open(path_to_image, "rb") as f:
            encoded_image = base64.b64encode(f.read())
        encoded_image_text = encoded_image.decode("utf-8")
        base64_qwen = f"data:image/jpeg;base64,{encoded_image_text}"

        content = [{
                    "type": "image_url",
                    "image_url": {
                        "url": base64_qwen
                    },
                },
                {"type": "text", "text": prompt},]
        new_messages = [{
                "role": "user",
                "content": content
        }]

        return new_messages

class Claude_Vision_agent_full_prompt(Llama_32_agent_full_prompt):
    @backoff.on_exception(
    backoff.expo, Exception,
    on_backoff=handle_backoff,
    on_giveup=handle_giveup,
    max_tries=1
    )
    def act(self, messages: List[Dict[str, Any]]) -> str:
        time.sleep(0.5)
        messages = self.format_message(messages)
        url = "https://oneapi.lo-li.co/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-EEK9aJ3fd0sz4zZ4B147268419D7462cBb565a10A2C48108"
        }

        data = {
            'model': self.name,
            #'model': "Llama-3.2-11B-Vision-Instruct",
            'messages': messages,
            #'seed': 34,
            'temperature': self.temperature,
            'stream': False
        }


        response = requests.post(url, headers=headers, json=data)

        #print(response)
        if response.status_code != 200:
            print(response.text)

        return response.json()["choices"][0]["message"]["content"]
    
    def format_message(self, messages):
        # TODO: support note and observation
        history = []
        images = []
        
        for message in messages:
            if message["role"] == "user":
                if isinstance(message["content"], str):
                    continue
                for content in message["content"]:
                    if content.get("image_url"):
                        images.append(content["image_url"]["url"])
        #window_size = Image.open(images[0]).size
        #images = [open(image, "rb") for image in images]
        instruction = messages[0]["content"].replace("<image>","")
        system_prompt = "<|system|>\n" + self.system_prompt(instruction) + "\n\n"
        
        index = len([message for message in messages if message["role"] == "user"]) - 1
        status = messages[-1]["content"][0]["text"] if index > 0 else "{}"
        if index == 0:
            current_turn = f"Round {index}\n\n<|user|>{instruction}\n\n{status}<|assistant|>\n"
        else:
            current_turn = f"Round {index}\n\n<|user|>** SCREENSHOT **\n\n{status}<|assistant|>\n"
        for i in range(index - 1, -1, -1):
            turn = messages[i * 2 + 2]
            text = turn["content"] if isinstance(turn["content"], str) else turn["content"][0]["text"]
            #text = format_response(text, window_size)
            if i == 0:
                processed_turn_text = f"Round {i}\n\n<|user|>{instruction}<|assistant|>\n{text}"
            else:
                processed_turn_text = f"Round {i}\n\n<|user|>** SCREENSHOT **<|assistant|>\n{text}"
            length = len(self.tokenizer.tokenize(
                "\n\n".join([system_prompt,
                             "** Earlier trajectory has been truncated **", processed_turn_text] + history + [
                                current_turn])))
            if (length > 8192 - 2304 - 50 - 512):
                history = ["** Earlier trajectory has been truncated **"] + history
                # print(f"Task {self.task_id} truncated at turn {index} due to length ({length}).")
                break
            else:
                history = [processed_turn_text] + history
        history.append(current_turn)
        prompt = "\n\n".join(history).lstrip("\n")
        prompt = system_prompt + prompt
        path_to_image = images[0]

        with open(path_to_image, "rb") as f:
            encoded_image = base64.b64encode(f.read())
        encoded_image_text = encoded_image.decode("utf-8")
        base64_qwen = f"data:image/jpeg;base64,{encoded_image_text}"

        content = [{
                    "type": "image_url",
                    "image_url": {
                        "url": base64_qwen
                    }
                },
                {"type": "text", "text": prompt},]
        new_messages = [{
                "role": "user",
                "content": content
        }]

        return new_messages


class Swift_agent(Llama_32_agent):
    def add_system_prompt(self, prompt):
        return prompt
    
    @backoff.on_exception(
        backoff.expo, Exception,
        on_backoff=handle_backoff,
        on_giveup=handle_giveup,
        max_tries=10
    )
    def act(self, messages: List[Dict[str, Any]]) -> str:
        proxy = {
            'http': 'socks5h://127.0.0.1:8889',
            'https': 'socks5h://127.0.0.1:8889'
        }
        headers = {
            'Authorization': f'Bearer EMPTY',
            'Content-Type': 'application/json'
        }

        messages = self.format_message(messages)

        data = {
            "model": self.name,
            "messages": messages,
            #"stream": False,
            #"max_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            #"do_sample": False if self.temperature == 0 else True,
        }
        # print(messages)
        
        try:
            response = requests.post(f"{self.url}", headers=headers, data=json.dumps(data), proxies=proxy)
            print(response.text)
            response = response.json()
        except Exception as e:
            import traceback
            traceback.print_exc()
            return str(e)

        if "error" in response:
            return response["error"]["message"]

        result = response.get("choices", [{}])[0].get("message", "").get("content", "").replace("<|begin_of_text|>","")
        return result

class Swift_agent_full_prompt(Swift_agent):
    def format_message(self, messages):
        # TODO: support note and observation
        history = []
        images = []
        
        for message in messages:
            if message["role"] == "user":
                if isinstance(message["content"], str):
                    continue
                for content in message["content"]:
                    if content.get("image_url"):
                        images.append(content["image_url"]["url"])
        #window_size = Image.open(images[0]).size
        #images = [open(image, "rb") for image in images]
        instruction = messages[0]["content"].replace("<image>","")
        system_prompt = "<image><|system|>\n" + self.system_prompt(instruction) + "\n\n"
        
        index = len([message for message in messages if message["role"] == "user"]) - 1
        status = messages[-1]["content"][0]["text"] if index > 0 else "{}"
        if index == 0:
            current_turn = f"Round {index}\n\n<|user|>{instruction}\n\n{status}<|assistant|>\n"
        else:
            current_turn = f"Round {index}\n\n<|user|>** SCREENSHOT **\n\n{status}<|assistant|>\n"
        for i in range(index - 1, -1, -1):
            turn = messages[i * 2 + 2]
            text = turn["content"] if isinstance(turn["content"], str) else turn["content"][0]["text"]
            #text = format_response(text, window_size)
            if i == 0:
                processed_turn_text = f"Round {i}\n\n<|user|>{instruction}<|assistant|>\n{text}"
            else:
                processed_turn_text = f"Round {i}\n\n<|user|>** SCREENSHOT **<|assistant|>\n{text}"
            length = len(self.tokenizer.tokenize(
                "\n\n".join([system_prompt,
                             "** Earlier trajectory has been truncated **", processed_turn_text] + history + [
                                current_turn])))
            if (length > 8192 - 2304 - 50 - 512):
                history = ["** Earlier trajectory has been truncated **"] + history
                # print(f"Task {self.task_id} truncated at turn {index} due to length ({length}).")
                break
            else:
                history = [processed_turn_text] + history
        history.append(current_turn)
        prompt = "\n\n".join(history).lstrip("\n")
        prompt = system_prompt + prompt
        path_to_image = images[0]
        with open(path_to_image, "rb") as f:
            encoded_image = base64.b64encode(f.read())
        encoded_image_text = encoded_image.decode("utf-8")
        base64_qwen = f"data:image;base64,{encoded_image_text}"


        content = [{
                    "type": "image_url",
                    "image_url": {
                        "url": base64_qwen
                    },
                },
                {"type": "text", "text": prompt},]
        new_messages = [{
                "role": "user",
                "content": content
        }]

        return new_messages

if __name__ == "__main__":
    agent = Qwen2VLAgent("http://172.18.192.104:10011/v1/chat/completions")
    path_to_image = "/raid/xuyifan/Android-Lab-main/logs/evaluation/glm4-9b/bluecoins_1_2024-09-29_14-15-04/Screen/screenshot-0-1727633757.7619846-before.png"
    with open(path_to_image, "rb") as f:
        encoded_image = base64.b64encode(f.read())
    encoded_image_text = encoded_image.decode("utf-8")
    base64_qwen = f"data:image;base64,{encoded_image_text}"
    content = [{
                    "type": "image_url",
                    "image_url": {
                        "url": base64_qwen
                    },
                },
                {"type": "text", "text": "What is the text in the illustrate?"},]
    message = {
            "role": "user",
            "content": content
    }
    print(agent.act(message))
