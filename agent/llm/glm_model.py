import sys
sys.path.append('/raid/xuyifan/Android-Lab-xml/Android-Lab-main')
from agent.model import *
import time
import json


class GLMModelAgent(OpenAIAgent):
    def __init__(self, api_base: str, max_tokens: int = 512, temperature = 0.001, **kwargs):
        super().__init__()
        self.name = "GLMModelAgent"
        self.api_base = api_base
        self.max_tokens = max_tokens
        self.temperature = temperature

    @backoff.on_exception(
        backoff.expo, Exception,
        on_backoff=handle_backoff,
        on_giveup=handle_giveup,
        max_tries=10
    )
    def act(self, messages: List[Dict[str, Any]] = None, prefix=None, prompt=None) -> str:
        time.sleep(0.2)
        if messages is not None:
            prompt = self.format_prompt(messages, prefix=prefix)
        data = {
            "stream": False,
            "inputs": prompt,
            "parameters": {
                "do_sample": False if self.temperature < 0.001 else True,
                "max_new_tokens": self.max_tokens,
                "seed": 34,
                "temperature": self.temperature,
                "stop": ["<|endoftext|>", "<|user|>", "<|observation|>"]
            }
        }

        # 将数据转换为 JSON 字符串
        json_data = json.dumps(data)
        proxy = {
        'http': 'socks5h://127.0.0.1:8889',
        'https': 'socks5h://127.0.0.1:8889'
        }

        # 设置请求头
        headers = {'Content-Type': 'application/json'}

        # 发起 POST 请求
        # response = requests.post('http://172.19.128.80:8080', data=json_data, headers=headers).json()
        response = requests.post(self.api_base, data=json_data, proxies=proxy, headers=headers).json()
        # print(response[0])
        # import pdb; pdb.set_trace()
        # 打印响应内容
        print(response)
        # print(response.json()[0]['generated_text'])
        print(response[0])
        if '</s>' in response[0]['generated_text']:
            rsp = response[0]['generated_text'].replace('</s>', '')
        else:
            rsp = response[0]['generated_text']
        print(rsp)
        return rsp

    def format_prompt(self, messages: List[Dict[str, Any]], prefix=None) -> str:
        history = ""
        turn = 0
        for message in messages:
            if message == messages[-1]:
                break
            if message["role"] == "assistant":
                history += f"Round {turn}\n\n<|user|>\n** XML **\n\n<|assistant|>\n{message['content']}\n\n"
                turn = turn + 1

        if messages[-1].get("current_app"):
            current_app_name = messages[-1]['current_app']
            current_turn = f"Round {turn}\n\n<|user|>\n{json.dumps({'current_app': current_app_name}, ensure_ascii=False)}\n{messages[-1]['content']}\n\n<|assistant|>\n"
        else:
            current_turn = f"Round {turn}\n\n<|user|>\n{messages[-1]['content']}\n\n<|assistant|>\n"
        prompt = history + current_turn
        if prefix is not None:
            prompt = prefix + "\n\n" + prompt
        elif prefix is None and messages[0].get("role") == "system":
            prompt = messages[0].get("content") + "\n\n" + prompt

        return prompt


class GLMModelAgent_0801(GLMModelAgent):
    def format_prompt(self, messages: List[Dict[str, Any]], prefix=None) -> str:
        history = ""
        turn = 0
        instruction = messages[0].get("content").split("Task Instruction: ")[-1]
        for message in messages:
            if message == messages[-1]:
                break
            if message["role"] == "assistant":
                prompt = instruction if turn == 0 else "** XML **"
                # status = f"\n\n{json.dumps({'current_app': message['current_app']}, ensure_ascii=False)}" if message.get("current_app") else ""
                status = ""
                history += f"Round {turn}\n\n<|user|>\n{prompt}{status}\n\n<|assistant|>\n{message['content']}\n\n"
                turn = turn + 1

        status = json.dumps({'current_app': messages[-1]['current_app']}, ensure_ascii=False) if messages[-1].get("current_app") else ""
        prompt = instruction if turn == 0 else "** XML **"
        compressed_xml = messages[-1]['content'].replace('** XML **\n', '')
        current_turn = f"Round {turn}\n\n<|user|>\n{prompt}\n\n{status}\n{compressed_xml}\n\n<|assistant|>\n"
        prompt = history + current_turn
        # TODO: note and observation not added yet
        return prompt
    
class LLaMAModelAgent_0801(GLMModelAgent_0801):
    @backoff.on_exception(
        backoff.expo, Exception,
        on_backoff=handle_backoff,
        on_giveup=handle_giveup,
        max_tries=10
    )
    def act(self, messages: List[Dict[str, Any]] = None, prefix=None, prompt=None) -> str:
        time.sleep(0.2)
        if messages is not None:
            prompt = self.format_prompt(messages, prefix=prefix)
        proxy = {
        'http': 'socks5h://127.0.0.1:8889',
        'https': 'socks5h://127.0.0.1:8889'
        }
        #rl = f'http://localhost:{PORT}/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            # 'Host': ''
        }
        data = {
            'model': 'llama3-8b',
            'messages': [{"role": "user","content": prompt}],
            'seed': 34,
            "do_sample": False if self.temperature < 0.001 else True,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'stream': False
        }
        response = requests.post(self.api_base, headers=headers, json=data, proxies=proxy)
        return response.json()["choices"][0]["message"]["content"]

class LLaMAModelAgent_full_prompt(GLMModelAgent):
    @backoff.on_exception(
        backoff.expo, Exception,
        on_backoff=handle_backoff,
        on_giveup=handle_giveup,
        max_tries=10
    )
    def act(self, messages: List[Dict[str, Any]] = None, prefix=None, prompt=None) -> str:
        time.sleep(0.2)
        if messages is not None:
            prompt = self.format_prompt(messages, prefix=prefix)
        proxy = {
        'http': 'socks5h://127.0.0.1:8889',
        'https': 'socks5h://127.0.0.1:8889'
        }
        #rl = f'http://localhost:{PORT}/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            # 'Host': ''
        }
        data = {
            'model': 'llama3-8b',
            'messages': [{"role": "user","content": prompt}],
            'seed': 34,
            "do_sample": False if self.temperature < 0.001 else True,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'stream': False
        }
        response = requests.post(self.api_base, headers=headers, json=data, proxies=proxy)
        return response.json()["choices"][0]["message"]["content"]
    
class Claude_35_full_prompt(LLaMAModelAgent_full_prompt):
    def __init__(self, model_name,max_tokens: int = 512, temperature = 0.001, **kwargs):
        #super().__init__()
        self.name = "ClaudeModelAgent"
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

    @backoff.on_exception(
        backoff.expo, Exception,
        on_backoff=handle_backoff,
        on_giveup=handle_giveup,
        max_tries=10
    )
    def act(self, messages: List[Dict[str, Any]] = None, prefix=None, prompt=None) -> str:
        time.sleep(0.2)
        if messages is not None:
            prompt = self.format_prompt(messages, prefix=prefix)
        url = "https://oneapi.lo-li.co/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-EEK9aJ3fd0sz4zZ4B147268419D7462cBb565a10A2C48108"
        }
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": self.model_name,
            "stream": False
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"]


class LLaMAModelAgent_0801_tgi(GLMModelAgent_0801):
    @backoff.on_exception(
        backoff.expo, Exception,
        on_backoff=handle_backoff,
        on_giveup=handle_giveup,
        max_tries=10
    )
    def act(self, messages: List[Dict[str, Any]] = None, prefix=None, prompt=None) -> str:
        time.sleep(0.2)
        if messages is not None:
            prompt = self.format_prompt(messages, prefix=prefix)
        base_url = "http://172.18.196.246:3000"
        proxy = {
        'http': 'socks5h://127.0.0.1:8889',
        'https': 'socks5h://127.0.0.1:8889'
        }
        payload = {
                "inputs": prompt,
                "parameters": {
                    "return_full_text": False,
                    "do_sample": False,
                    "max_new_tokens": 256,
                    "decoder_input_details": False,
                    "details": False,
                    "stop": [
                    "</s>",
                    "<|endoftext|>",
                    "<|user|>",
                    "<|observation|>"
                    ]
                },
                "stream": False
            }
        headers = { 'Content-Type': 'application/json' }

        try:
            response = requests.post(base_url, headers=headers, json=payload, verify=False, proxies=proxy)
            response = response.json()
            if 'error' in response:
                raise Exception(f"{response['error']}")
            # print('----{}----'.format(response[0]['generated_text']))
            return response[0]['generated_text']

        except Exception as e:
            print(e)
            payload['inputs'] = prompt[:30000]
            response = requests.post(base_url, headers=headers, json=payload, verify=False, proxies=proxy)
            response = response.json()
            if 'error' in response:
                raise Exception(f"{response['error']}")
            return response[0]['generated_text']
        
if __name__ == "__main__":
    agent = GLMModelAgent_0801(api_base="http://172.18.196.246:3000")

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Please response concisely."
        },
        {
            "role": "user",
            "content": "Tell me a story."
        }
    ]
    print(agent.act(messages))