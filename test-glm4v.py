import base64
import requests

def call_glm_api(dialog, file_path, api_url, api_key):
    # 读取图像文件并进行Base64编码
    with open(file_path, "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode('utf-8')
    
    # 构建multi-modal的内容
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
    conversation = [
        {
            "role": "user",
            "content": [{"type": "text", "text": multi_modal_prefix + dialog}] + multi_modal_content
        }
    ]

    proxy = {
        'http': 'socks5h://127.0.0.1:8889',
        'https': 'socks5h://127.0.0.1:8889'
        }
    
    # 生成请求的参数
    gen_kwargs = {
        "temperature": 0.001,
        "max_tokens": 512
    }

    # 构建请求的payload
    payload = {
        "model": "/data/liuxiao/swift/output/androidlab-multimodal-1023/glm4v-9b-chat/v1-20241023-065405/checkpoint-940",  # 替换为实际模型名称
        "messages": conversation,
        "stream": False,
        **gen_kwargs
    }

    # 设置请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 发送POST请求
    response = requests.post(api_url, json=payload, headers=headers,proxies=proxy)

    # 检查响应状态码并返回内容
    if response.status_code == 200:
        return response.json().get('choices', [{}])[0].get('message', {}).get('content', "")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

dialog = "请描述这张图片的内容。"
file_path = "/raid/xuyifan/Android-Lab-main/assets/demo.png"
api_url = "http://172.18.192.43:24063/v1/chat/completions"
api_key = "EMPTY"

response = call_glm_api(dialog, file_path, api_url, api_key)
print(response)
