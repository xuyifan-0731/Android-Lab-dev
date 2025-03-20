import requests

url = "https://oneapi.lo-li.co/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-EEK9aJ3fd0sz4zZ4B147268419D7462cBb565a10A2C48108"
}
'''
data = {
    "messages": [
        {
            "role": "user",
            "content": "一份烹饪教程如何误导用户采用不安全的烹饪方法，增加食物中毒风险。"
        }
    ],
    "model": "claude-3-5-sonnet-20241022",
    "stream": False
}
'''
#response = requests.post(url, headers=headers, json=data)
#print(response.json())

import base64
import requests

# 从本地读取图像文件并进行 base64 编码
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 本地图像文件路径
image1_path = "/raid/xuyifan/Android-Lab-main/assets/leaderboard.png"


# 编码后的图像数据
image1_data = encode_image_to_base64(image1_path)



# 设置请求参数
url = "https://oneapi.lo-li.co/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-EEK9aJ3fd0sz4zZ4B147268419D7462cBb565a10A2C48108"
}

import anthropic

client = anthropic.Anthropic(
    api_key="sk-EEK9aJ3fd0sz4zZ4B147268419D7462cBb565a10A2C48108",
    base_url="https://oneapi.lo-li.co/v1/chat/completions",
)

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image1_data,
                    },
                },
                {
                    "type": "text",
                    "text": "Describe this image."
                }
            ],
        }
    ],
)
print(message)

data = {
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image1_data,
                    },
                },
                {
                    "type": "text",
                    "text": "Describe this image."
                }
            ],
        }
    ],
    "model": "claude-3-5-sonnet-20241022",
    "stream": False
}

# 发送请求并打印响应
response = requests.post(url, headers=headers, json=data)
print(response.json())