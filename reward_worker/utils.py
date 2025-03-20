import base64
import copy
import backoff
from zhipuai import ZhipuAI


def build_android_prompt_gpt_with_image(
    instruction, response, last_actions
) -> tuple[str, str]:
    # COMBINED image
    system_msg = """You are an expert in evaluating the performance of an android navigation agent. The agent is designed to help a human user navigate the device to complete a task. Given the user's instruction, and all screenshots of the agent execute the task, your goal is to decide whether the agent has successfully completed the task or not.

All screenshots of the task are stitched together in the image. You must go through all the screenshots one by one.

CAREFUL! You need to pay more attention to the image than to the agent's finish message, because the agent might be hallucinating!

*IMPORTANT*
Format your response into two lines as shown below:

Thoughts: <your thoughts and reasoning process>"
Status: "YES" or "NO"
"""
# Please output only this trajectory judgement as "YES" or "NO".
# """

    prompt = f"""User Instruction: {instruction}

Action History:
{last_actions}

Bot response to the user: {response if response else "N/A"}. 
"""

#     # FINAL image
#     system_msg = """You are an expert in evaluating the performance of an android navigation agent. The agent is designed to help a human user navigate the device to complete a task. Given the user's instruction, and the screenshot of the end of task execution, your goal is to decide whether the agent has successfully completed the task or not.

# CAREFUL! You need to pay more attention to the image than to the agent's finish message, because the agent might be hallucinating!

# *IMPORTANT*
# Format your response into two lines as shown below:

# Thoughts: <your thoughts and reasoning process>"
# Status: "YES" or "NO"
# """
#     prompt = f"""User Instruction: {instruction}

# Action History:
# {last_actions}

# Bot response to the user: {response if response else "N/A"}. 
# """
    return prompt, system_msg


def build_android_prompt_gpt_with_xml(
    instruction, response, last_actions, final_xml
) -> tuple[str, str]:
    system_msg = """You are an expert in evaluating the performance of an android navigation agent. The agent is designed to help a human user navigate the device to complete a task. Given the user's instruction, and the XML of the end-of-task screen, your goal is to decide whether the agent has successfully completed the task or not.

CAREFUL! You need to pay more attention to the XML than to the agent's finish message, because the agent might be hallucinating!

*IMPORTANT*
Format your response into two lines as shown below:

Thoughts: <your thoughts and reasoning process>"
Status: "YES" or "NO"
"""
    prompt = f"""User Instruction: {instruction}

Action History:
{last_actions}

XML of the end-of-task screen:
{final_xml}

Bot response to the user: {response if response else "N/A"}. 
"""
    return prompt, system_msg


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def replace_image_url(messages, throw_details=False, keep_path=False):
    new_messages = copy.deepcopy(messages)
    for message in new_messages:
        if message["role"] == "user":
            for content in message["content"]:
                if isinstance(content, str):
                    continue
                if content["type"] == "image_url":
                    image_url = content["image_url"]["url"]
                    image_url_parts = image_url.split(";base64,")
                    if not keep_path:
                        content["image_url"]["url"] = (
                            image_url_parts[0]
                            + ";base64,"
                            + image_to_base64(image_url_parts[1])
                        )
                    else:
                        content["image_url"]["url"] = f"file://{image_url_parts[1]}"
                    if throw_details:
                        content["image_url"].pop("detail", None)
    return new_messages


def extract_content(text, start_tag):
    """
    Extract the content that follows 'Info:' in a given string.

    :param text: A string that may contain lines starting with 'Info:'
    :return: The content that follows 'Info:' or None if not found
    """
    # Split the text into lines
    lines = text.split("\n\n")
    if len(lines) == 1:
        lines = text.split("\n")

    if len(lines) != 2:
        print(f"Unexpected number of lines: {len(lines)}")
        for idx, line in enumerate(lines):
            print(f"Line {idx + 1}: {line}")

    # Loop through each line to find a line that starts with 'Info:'
    for line in lines:
        if line.startswith(start_tag):
            # Extract and return the content after 'Info:'
            return line[len(start_tag) :].strip()

    # Return None if 'Info:' is not found in any line
    return ""

def handle_backoff(details):
    print(f"Retry {details['tries']} for Exception: {details['exception']}")

def handle_giveup(details):
    print(
        "Backing off {wait:0.1f} seconds afters {tries} tries calling fzunction {target} with args {args} and kwargs {kwargs}".format(
            **details
        )
    )

@backoff.on_exception(
    backoff.expo,
    Exception,  # 捕获所有异常
    max_tries=5,
    on_backoff=handle_backoff,  # 指定重试时的回调函数
    giveup=handle_giveup,
)  # 指定放弃重试时的回调函数
def get_glm_completion(model, messages, glm4_key="4082fe4403895d0c81a7509768c11765.PXCBHyjjA49QILBQ"):
    client = ZhipuAI(api_key=glm4_key)
    response = client.chat.completions.create(
        model=model,  # 填写需要调用的模型名称
        messages=messages,
    )
    return response.choices[0].message.content
