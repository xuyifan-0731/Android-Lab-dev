import requests

proxy = {
    'http': 'socks5h://127.0.0.1:8889',
    'https': 'socks5h://127.0.0.1:8889'
}

headers = {
    'Content-Type': 'application/json',
}

data = {
    'model': "qwen2-vl-7b",
    'messages': [
        {"role": "user", "content": "你好"}
    ],
    'seed': 34,
    'temperature': 0.01,
    'top_p': 0.95,
    'max_tokens': 256,
    'stream': False,
}

response = requests.post(
    "http://172.18.199.22:9001/v1/chat/completions",
    headers=headers,
    json=data,
    proxies=proxy,
    timeout=300  # Optional timeout
)
response.raise_for_status()
resp_json = response.json()
print(resp_json)