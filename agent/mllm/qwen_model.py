from http import HTTPStatus

import dashscope

from agent.model import *
import json


class QwenAgent(OpenAIAgent):
    def __init__(
            self,
            api_key: str,
            model_name: str = "qwen-vl-max",
            seed: int = 42,
            top_k: float = 1.0,
            sleep: int = 2
    ):
        dashscope.api_key = api_key
        self.name = "QwenAgent"
        self.model = model_name
        self.seed = seed
        self.top_k = top_k
        self.sleep = sleep

    @backoff.on_exception(
        backoff.expo, Exception,
        on_backoff=handle_backoff,
        on_giveup=handle_giveup,
        max_tries=10
    )
    def act(self, messages: List[Dict[str, Any]]) -> str:
        messages = self.format_message(messages)
        print(messages)
        response = dashscope.MultiModalConversation.call(model=self.model, messages=messages, seed=self.seed,
                                                         top_k=self.top_k)

        if response.status_code == HTTPStatus.OK:
            print(f"Prompt Tokens: {response.usage.input_tokens}\nCompletion Tokens: {response.usage.output_tokens}\n")
            return response.output.choices[0].message.content[0]['text']
        else:
            print(response.code, response.message)
            for message in messages:
                print(message)
            return response.code, response.message  # The error code & message

    def format_message(self, message):
        if message[0]["role"] == "system":
            message[-1]["content"][0]["text"] = message[0]["content"]
        return [message[-1]]

    def prompt_to_message(self, prompt, images):
        content = [{
            "text": prompt
        }]
        for img in images:
            img_path = f"file://{img}"
            content.append({
                "image": img_path
            })
        message = {
            "role": "user",
            "content": content
        }
        return message


class QwenVLAgent(Agent):
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
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.kwargs = kwargs
        self.name = "QwenVLAgent"

    @backoff.on_exception(
        backoff.expo, Exception,
        on_backoff=handle_backoff,
        on_giveup=handle_giveup,
        max_tries=10
    )
    def act(self, messages: List[Dict[str, Any]]) -> str:
        messages = self.format_messages(messages)
        
        proxy = {
            'http': 'socks5h://127.0.0.1:8889',
            'https': 'socks5h://127.0.0.1:8889'
        }
        
        headers = {
            'Content-Type': 'application/json',
        }
        
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
            self.api_base,
            headers=headers,
            json=data,
            proxies=proxy,
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
        base_text = prompt + f"\n\n{json.dumps({'current_app': current_app}, ensure_ascii=False)}"
        final_text = base_text + (f"\n{clean_tree_structure(xml)}" if xml is not None else "")
        content = [
            {
                "type": "text",
                "text": final_text
            }
        ]
        
        for img in images:
            base64_img = image_to_base64(img)
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
    