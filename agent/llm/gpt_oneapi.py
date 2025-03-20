from agent.model import *
import json

class OpenAIAgent_oneapi(Agent):
    def __init__(
            self,
            api_key: str = '',
            api_base: str = '',
            model_name: str = '',
            max_new_tokens: int = 16384,
            temperature: float = 0,
            top_p: float = 0.7,
            **kwargs
    ) -> None:
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        # openai.api_base = api_base
        # openai.api_key = api_key
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.kwargs = kwargs
        self.name = "OpenAIAgent"

        self.base_url = "https://one-api.glm.ai/v1/chat/completions"
        self.api_key = "sk-iKDxVf6Uap69SsSUBbC642C48f8e44Ce861f2941CcE278Ab"

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
        payload = json.dumps({
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_new_tokens
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.api_key}"
        }
        response = requests.request("POST", self.base_url, headers=headers, data=payload, timeout=100,proxies=proxy).json()
        print(response)
        return response['choices'][0]['message']['content']

    def prompt_to_message(self, prompt, images):
        content = [
            {
                "type": "text",
                "text": prompt
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

    def system_prompt(self, instruction) -> str:
        return SYSTEM_PROMPT_ANDROID_MLLM_DIRECT + f"\n\nTask Instruction: {instruction}"
