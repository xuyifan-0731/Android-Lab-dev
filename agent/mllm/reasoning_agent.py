from agent.mllm.qwen_model import QwenVLAgent
import copy
import json
from typing import List, Dict, Any


system_prompt = '''# Setup
You are a professional Android operation agent assistant that can fulfill the user's high-level instructions. Given a screenshot of the Android interface at each step, you first analyze the situation, then plan the best course of action using Python-style pseudo-code.

# More details about the code
Your response format must be structured as follows:

Think first: Use <think>...</think> to analyze the current screen, identify key elements, and determine the most efficient action.
Provide the action: Use <ans>...</ans> to return a single line of pseudo-code representing the operation.

The output example is as follows:
<think>
[Your throught]
</think>
<ans>
[Your operation code]
</ans>

- **Tap**  
  Perform a tap action on a specified screen area. The element is a list of 4 integers, representing the coordinates of the top-left and bottom-right corners of the rectangle. You must choose one element from the current state.
  **Example**:  
  <think>
  [Your throught]
  </think>
  <ans>
  do(action="Tap", element=[100, 200, 150, 250])
  </ans>
- **Type**  
  Enter text into the currently focused input field.  
  **Example**:  
  <think>
  [Your throught]
  </think>
  <ans>
  do(action="Type", text="Hello World")
  </ans>
- **Swipe**  
  Perform a swipe action in a specified direction (`"up"`, `"down"`, `"left"`, `"right"`).   
  The swipe distance can be `"long"`, `"medium"` (default), or `"short"`.  
  You can add the element to the action to specify the swipe area. The element is a list of 4 integers, representing the coordinates of the top-left and bottom-right corners of the rectangle. You must choose one element from the current state.
  **Examples**:  
  <think>
  [Your throught]
  </think>
  <ans>
  do(action="Swipe", direction="up", dist="long", element=[100, 200, 150, 250])
  </ans>
- **Long Press**  
  Perform a long press action on a specified screen area.  
  You can add the element to the action to specify the long press area. The element is a list of 4 integers, representing the coordinates of the top-left and bottom-right corners of the rectangle. You must choose one element from the current state.
  **Example**:  
  <think>
  [Your throught]
  </think>
  <ans>
  do(action="Long Press", element=[200, 300, 250, 350])
  </ans>
- **Launch**  
  Launch an app. Try to use launch action when you need to launch an app. Check the instruction to choose the right app before you use this action.
  **Example**:  
  <think>
  [Your throught]
  </think>
  <ans>
  do(action="Launch", app="Settings")
  </ans>
- **Back**  
  Press the Back button to navigate to the previous screen.  
  **Example**:  
  <think>
  [Your throught]
  </think>
  <ans>
  do(action="Back")
  </ans>
- **Finish**  
  Terminate the program and optionally print a message.  
  **Example**:  
  <think>
  [Your throught]
  </think>
  <ans>
  finish(message="Task completed.")
  </ans>


REMEMBER: 
- Think before you act: Always analyze the current UI and the best course of action before executing any step, and output in <think> part.
- Only ONE LINE of action in <ans> part per response: Each step must contain exactly one line of executable code.
- Generate execution code strictly according to format requirements.
- A screenshot of the current page and the UI location information will be provided at the same time. If your action involves location information, try to choose the known UI location information.
- Thinking part in history is omitted, you should output the thinking part in your response.

Output Example:
<think>
[Your throught]
</think>
<ans>
[Your operation code]
</ans>'''

class QwenVLAgent_reasoning(QwenVLAgent):
    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        messages = copy.deepcopy(messages)
        
        if messages[0]["role"] == "system":
            instruction = messages[0]["content"]
            messages = messages[1:]
            if isinstance(messages[0]["content"], str):
                messages[0]["content"] = messages[0]["content"].replace("** XML **", instruction)
            else:
                messages[0]["content"][0]["text"] = messages[0]["content"][0]["text"].replace("** XML **", instruction)
        system_message = {"role": "system", "content": system_prompt}
        messages.insert(0, system_message)
        for i, message in enumerate(messages):
            if 'current_app' in message:
                current_app = message.pop("current_app")
            
            if isinstance(message["content"], str):
                message["content"] = message["content"].replace("** XML **", "** Screen Info **")
                if message["role"] == "assistant" and isinstance(messages[i-1]["content"], str):
                    messages[i-1]["content"] += f"\n\n{json.dumps({'current_app': current_app}, ensure_ascii=False)}"
            else:
                message["content"][0]["text"] = message["content"][0]["text"].replace("** XML **", "** Screen Info **")
                
            if message["role"] == "assistant" and "<think>" not in message["content"]:
                message["content"] = "<think>\nRound Thought Records is ommitted...\n</think>\n<ans>\n" + message["content"] + "\n</ans>"
                
        

        return messages