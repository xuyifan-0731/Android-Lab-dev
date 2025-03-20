from http import HTTPStatus

import dashscope

from agent.model import *
import json
import requests
from PIL import Image
import io
import math


def smart_resize(
        t: int, h: int, w: int, t_factor: int = 2, h_factor: int = 28, w_factor: int = 28,
        min_pixels: int = 112 * 112, max_pixels: int = 23520000,
):
    """
    copy from qwen2vl
https://github.com/huggingface/transformers/src/transformers/models/qwen2_vl/image_processing_qwen2_vl.py
    Rescales the image so that the following conditions are met:

    1. Both dimensions (h and w) are divisible by 'factor'.

    2. The total number of pixels is within the range ['min_pixels', 'max_pixels'].

    3. The aspect ratio of the image is maintained as closely as possible.

    """
    assert t >= t_factor, 'Temporal dimension must be greater than the factor.'
    h_bar = round(h / h_factor) * h_factor
    w_bar = round(w / w_factor) * w_factor
    t_bar = round(t / t_factor) * t_factor

    if t_bar * h_bar * w_bar > max_pixels:
        beta = math.sqrt((t * h * w) / max_pixels)
        h_bar = math.floor(h / beta / h_factor) * h_factor
        w_bar = math.floor(w / beta / w_factor) * w_factor
    elif t_bar * h_bar * w_bar < min_pixels:
        beta = math.sqrt(min_pixels / (t * h * w))
        h_bar = math.ceil(h * beta / h_factor) * h_factor
        w_bar = math.ceil(w * beta / w_factor) * w_factor

    return h_bar, w_bar

def load_image_to_base64_image(image_path):
    if image_path.startswith("data:image/"):
        image_data = base64.b64decode(image_path.split(",")[1])
    else:
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()

    # 将图像数据读入Pillow图像对象
    ####################################
    # SMART RESIZE
    image = Image.open(io.BytesIO(image_data))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    # 原始图像的高度和宽度
    w, h = image.size

    # 计算新的尺寸
    h_bar, w_bar = smart_resize(1, h, w, t_factor=1, max_pixels=1000384)
    # 调整图像大小
    image = image.resize((w_bar, h_bar), Image.Resampling.BICUBIC)

    # 将调整大小后的图像保存为字节数据
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    buffered.seek(0)
    image_data = buffered.getvalue()
    ####################################

    base64_encoded_data = base64.b64encode(image_data)
    image_base64 = base64_encoded_data.decode('utf-8')
    return image_base64


class GLM4VAgent(Agent):
    def __init__(
            self,
            api_base: str = 'http://172.18.199.22:9000/v1',
            model_name: str = 'qwen2-vl-7b',
            max_new_tokens: int = 256,
            temperature: float = 0,
            top_p: float = 0.95,
            **kwargs
    ) -> None:
        self.api_base = api_base
        # self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.kwargs = kwargs
        self.name = "GLM4VAgent"
        self.headers = {
            'Content-Type': 'application/json',
        }
        self.proxy = {
            'http': 'socks5h://127.0.0.1:8889',
            'https': 'socks5h://127.0.0.1:8889'
        }
        try:
            response = requests.get(
                f"{self.api_base}/models",
                headers=self.headers,
                proxies=self.proxy,
                timeout=2
            )
            response.raise_for_status()
            models = response.json()
            self.model_name = models['data'][0]['id']
        except Exception as e:
            raise f"Failed to get model name: {e}"

    @backoff.on_exception(
        backoff.expo, Exception,
        on_backoff=handle_backoff,
        on_giveup=handle_giveup,
        max_tries=10
    )
    def act(self, messages: List[Dict[str, Any]]) -> str:
        messages = self.format_messages(messages)
        
        data = {
            'model': self.model_name,
            'messages': messages,
            'seed': 34,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'max_tokens': self.max_new_tokens,
            'stream': False,
        }
        
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=self.headers,
            json=data,
            proxies=self.proxy,
            timeout=300  # Optional timeout
        )
        response.raise_for_status()
        resp_json = response.json()
        return resp_json["choices"][0]["message"]["content"]
    
    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        messages = copy.deepcopy(messages)
        if messages[0]["role"] == "system":
            instruction = messages[0]["content"]
            messages = messages[1:]
            if isinstance(messages[0]["content"], str):
                messages[0]["content"] = messages[0]["content"].replace("** XML **", instruction)
            else:
                messages[0]["content"][0]["text"] = messages[0]["content"][0]["text"].replace("** XML **", instruction)
            
        for i, message in enumerate(messages):
            if 'current_app' in message:
                current_app = message.pop("current_app")
            
            if isinstance(message["content"], str):
                message["content"] = message["content"].replace("** XML **", "** Screen Info **")
                if message["role"] == "assistant" and isinstance(messages[i-1]["content"], str):
                    messages[i-1]["content"] += f"\n\n{json.dumps({'current_app': current_app}, ensure_ascii=False)}"
            else:
                message["content"][0]["text"] = message["content"][0]["text"].replace("** XML **", "** Screen Info **")

        return messages

    def format_prompt(self, messages: List[Dict[str, Any]]) -> str:
        messages = self.format_messages(messages)
        for message in messages:
            if isinstance(message["content"], list):
                message["content"] = "<image>" + message["content"][0]["text"]
        return messages
                    
    def prompt_to_message(self, prompt: str, images: List[str], xml: str=None, current_app: str=None) -> Dict[str, Any]:
        multi_modal_prefix = "<|begin_of_image|><|image|><|end_of_image|>"
        base_text = prompt + f"\n\n{json.dumps({'current_app': current_app}, ensure_ascii=False)}"
        final_text = base_text + (f"\n{clean_tree_structure(xml)}" if xml is not None else "")
        content = [
            {
                "type": "text",
                "text": multi_modal_prefix + final_text
            }
        ]
        
        for img in images:
            base64_img = load_image_to_base64_image(img)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_img}"
                }
            })
        message = {
            "role": "user",
            "content": content
        }
        return message