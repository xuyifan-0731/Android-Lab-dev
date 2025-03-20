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

print(image1_data[:100])


# 设置请求参数
url = "https://oneapi.lo-li.co/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-EEK9aJ3fd0sz4zZ4B147268419D7462cBb565a10A2C48108"
}

data = {
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image1_data}"
                    }
                },
                {
                    "type": "text",
                    "text": "Describe this image."
                }
            ],
        }
    ],
    "model": "claude-3-5-sonnet-20241022",
    "stream": False,
    "temperature": 0.01,
}

# 发送请求并打印响应
response = requests.post(url, headers=headers, json=data)
print(response.status_code,response.text,response.json())