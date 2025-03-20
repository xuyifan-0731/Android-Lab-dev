import requests
import json

# 定义API信息
api_key = 'EMPTY'
base_url = 'http://172.18.192.104:10011/v1'

# 获取模型类型
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
proxy = {
            'http': 'socks5h://127.0.0.1:8889',
            'https': 'socks5h://127.0.0.1:8889'
        }


# use base64
import base64
with open('/raid/xuyifan/Android-Lab-main/logs/evaluation/glm-4-0520/bluecoins_3_2024-10-16_03-21-36/Screen/screenshot-0-1729063350.4084158-before.png', 'rb') as f:
    img_base64 = base64.b64encode(f.read()).decode('utf-8')
image_url = f'data:image/jpeg;base64,{img_base64}'

# 定义问题
query = '图中是什么'
messages = [{
    'role': 'user',
    'content': [
        {'type': 'image_url', 'image_url': {'url': image_url}},
        {'type': 'text', 'text': query},
    ]
}]

# 构建请求数据
data = {
    'model': "glm4v-9b-chat",
    'messages': messages,
    "temperature": 0
}

# 请求生成回答
chat_url = f'{base_url}/chat/completions'
resp = requests.post(chat_url, headers=headers, data=json.dumps(data), proxies=proxy)
print(resp.text)
# 获取并打印响应内容
response = resp.json()['choices'][0]['message']['content']
print(resp.text)
print(f'query: {query}')
print(f'response: {response}')

