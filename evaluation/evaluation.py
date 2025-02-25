import templates.seeact_screenshot_prompts as SeeActPrompts
import templates.seeact_xml_prompts as SeeActPrompts_xml
from evaluation.definition import *
from evaluation.utils import *
from templates import *
from templates.packages import package_dict_en


class AutoTask():
    def __init__(self, instruction, controller, page_executor, agent, record, command_per_step, **kwargs):
        self.controller = controller
        self.page_executor = page_executor
        self.agent = agent
        self.record = record
        self.kwargs = kwargs
        self.set_system_prompt(instruction)
        self.record.command_per_step = [command_per_step]
        # pimusic and map.me need ac to fetch xml
        if "map.me" in instruction or "pimusic" in instruction:
            self.accessibility = self.controller.check_ac_survive()
        else:
            self.accessibility = False

    def set_system_prompt(self, instruction):
        self.record.history = [{
            "role": "system",
            "content": self.agent.system_prompt(instruction)
        }]

    def run_step(self):
        self.record.update_before(controller=self.controller, need_screenshot=True, ac_status=self.accessibility)
        round_count = self.record.get_round_count()
        compressed_xml_json = self.record.get_latest_xml()

        prompt = f"" if round_count == 0 else "** XML **\n"
        try:
            current_message = {"role": "user", "content": prompt + compressed_xml_json}
            if self.agent.name == "GLMModelAgent":
                current_message["current_app"] = self.controller.get_current_activity()
            rsp = self.agent.act([*self.record.history, current_message])
        except Exception as e:
            print_with_color(f"Error: {e}", "red")
            self.record.update_error(output=rsp, error_message=str(e))

        exe_res = self.page_executor(get_code_snippet(rsp))
        self.record.update_after(exe_res, rsp)
        self.record.turn_number += 1


class TextOnlyTask(AutoTask):
    def set_system_prompt(self, instruction):
        self.record.history = [{
            "role": "system",
            "content": SYSTEM_PROMPT_ANDROID_TEXT_GPT + f"\n\nTask Instruction: {instruction}"
        }]

class Multi_ScreenshotTask(AutoTask):
    def run_step(self):
        self.record.update_before(controller=self.controller, need_screenshot=True, ac_status=self.accessibility,
                                  need_labeled=False)
        round_count = self.record.get_round_count()
        try:
            # format current message
            prompt = "** XML **"
            xml = self.record.get_latest_xml(self.controller)
            image_path = self.record.contents[-1]['image']
            if self.record.get_current_activity() not in package_dict_en:
                print_with_color(f"Current activity: {self.record.get_current_activity()} not in package_dict_en, task dir {self.record.xml_file_path}", "red")
                with open('new_activate.txt', 'a') as f:
                    f.write(f"Current activity: {self.record.get_current_activity()} not in package_dict_en, task dir {self.record.xml_file_path}\n")

            current_app = package_dict_en[self.record.get_current_activity()]
            current_message = self.agent.prompt_to_message(prompt, [image_path], xml=xml, current_app=current_app)
            
            # format last user message
            if len(self.record.contents) > 1:
                prompt = "** XML **"
                image_path = self.record.contents[-2]['image']
                current_app = self.record.contents[-2]['current_app']
                last_user = self.agent.prompt_to_message(prompt, [image_path], current_app=current_app)
                
                rsp = self.agent.act([*self.record.history[:-2], last_user, self.record.history[-1], current_message])
                format_prompt = self.agent.format_prompt([*self.record.history[:-2], last_user, self.record.history[-1], current_message])
            else:
                rsp = self.agent.act([*self.record.history, current_message]) 
                format_prompt = self.agent.format_prompt([*self.record.history, current_message])
        except Exception as e:
            print_with_color(f"Error: {e}", "red")
            import traceback
            traceback.print_exc()
            exit(1)
        
        exe_res = self.page_executor(get_code_snippet(rsp))
        self.record.update_after(exe_res, rsp, format_prompt)
        self.record.turn_number += 1
    
    def set_system_prompt(self, instruction):
        self.record.history = [{
            "role": "system",
            "content": instruction
        }]

class ScreenshotTask(TextOnlyTask):
    def run_step(self):
        self.record.update_before(controller=self.controller, need_screenshot=True, ac_status=self.accessibility,
                                  need_labeled=True)
        round_count = self.record.get_round_count()
        prompt = json.dumps({"current_app": self.controller.get_current_app()},
                                                         ensure_ascii=False)
        try:
            xml = self.record.get_latest_xml()
            image_path = self.record.labeled_current_screenshot_path
            current_message = self.agent.prompt_to_message(prompt, [image_path])
            rsp = self.agent.act([*self.record.history, current_message])

            print("Model Response: ", rsp)
            
            #rsp = input("Please input the response: ")
        except Exception as e:
            import traceback
            print(traceback.print_exc())
            # print_with_color(f"Error: {e}", "red")

        exe_res = self.page_executor(get_code_snippet(rsp))
        self.record.update_after(exe_res, rsp)
        self.record.turn_number += 1

    def set_system_prompt(self, instruction):
        self.record.history = [{
            "role": "system",
            "content": SYSTEM_PROMPT_ANDROID_MLLM_DIRECT + f"\n\nTask Instruction: {instruction}"
        }]


class CogAgentTask(TextOnlyTask):
    def run_step(self):
        self.record.update_before(controller=self.controller, need_screenshot=True, ac_status=self.accessibility,
                                  need_labeled=True)
        round_count = self.record.get_round_count()
        prompt = json.dumps({"current_app": self.controller.get_current_app()},
                                                         ensure_ascii=False)
        try:
            image_path = self.record.labeled_current_screenshot_path
            current_message = self.agent.prompt_to_message(prompt, [image_path])
            rsp = self.agent.act([*self.record.history, current_message])
        except Exception as e:
            import traceback
            print(traceback.print_exc())
            # print_with_color(f"Error: {e}", "red")

        exe_res = self.page_executor(get_code_snippet(rsp))
        self.record.update_after(exe_res, rsp)
        self.record.turn_number += 1

    def set_system_prompt(self, instruction):
        self.record.history = [{
            "role": "system",
            "content": SYSTEM_PROMPT_ANDROID_MLLM_CogAgent + f"\n\nTask Instruction: {instruction}"
        }]

class QwenVLAgentTask(ScreenshotTask):
    def set_system_prompt(self, instruction):
        self.record.history = [{
            "role": "system",
            "content": f"{instruction}<image>"
        }]


class ScreenshotReactTask(ScreenshotTask):
    def set_system_prompt(self, instruction):
        self.record.history = [{
            "role": "system",
            "content": SYSTEM_PROMPT_ANDROID_MLLM_DIRECT_REACT + f"\n\nTask Instruction: {instruction}"
        }]


class ScreenSeeActTask(TextOnlyTask):

    def set_system_prompt(self, instruction):
        self.record.history = [{
            "role": "system",
            "content": SeeActPrompts.QUERY_SYSTEM_PROMPT
        }]
        self.stage_one_record = []
        self.instruction = instruction

    def run_step(self):
        self.record.update_before(controller=self.controller, need_screenshot=True, ac_status=self.accessibility,
                                  need_labeled=False)
        round_count = self.record.get_round_count()
        try:
            xml_tree = self.record.get_latest_xml_tree()
            choices_list = extract_bounds(xml_tree)
            image_path = self.page_executor.current_screenshot
            system_prompt = SeeActPrompts.QUERY_SYSTEM_PROMPT
            query_user_prompt = SeeActPrompts.QUERY_USER_PROMPT.format(
                task=self.instruction,
                previous_actions=("\n\n".join(self.stage_one_record) or "None")
            )
            query_message = self.agent.prompt_to_message(query_user_prompt, [image_path])
            referring_user_prompt = SeeActPrompts.REFERRING_USER_PROMPT.format(
                option_prompt="\n".join(f"{item['key']} | {item['value']}" for item in choices_list)
            )

            messages = [
                {"role": "system", "content": system_prompt},
                query_message,
            ]

            # Stage 1. Query
            print(">> Stage 1. Query")
            with open("monitor.log", "w") as f:
                f.write(json.dumps(messages, indent=4))
            description = self.agent.act(messages)
            print(description, end="\n\n")
            with open("monitor.log", "w") as f:
                f.write(description)
            messages.append({"role": "assistant", "content": description})
            messages.append({"role": "user", "content": referring_user_prompt})

            # Stage 2. Referring
            print(">> Stage 2. Referring")
            with open("monitor.log", "w") as f:
                f.write(json.dumps(messages, indent=4))

            referring = self.agent.act(messages)
            print(referring, end="\n\n")
            with open("monitor.log", "w") as f:
                f.write(referring)


        except Exception as e:
            import traceback
            print(traceback.print_exc())
            # print_with_color(f"Error: {e}", "red")
            # exit(1)
        referring = referring.split("Final Answer:")[-1].strip()
        exe_res = self.page_executor(get_code_snippet(referring))
        self.stage_one_record.append(description)
        self.record.update_after(exe_res, description + "\n\n==========\n\n" + referring)
        self.record.turn_number += 1

class TextOnlySeeActTask(TextOnlyTask):

    def set_system_prompt(self, instruction):
        self.record.history = [{
            "role": "system",
            "content": SeeActPrompts_xml.QUERY_SYSTEM_PROMPT
        }]
        self.stage_one_record = []
        self.instruction = instruction

    def run_step(self):
        self.record.update_before(controller=self.controller, need_screenshot=True, ac_status=self.accessibility,
                                  need_labeled=False)
        round_count = self.record.get_round_count()
        try:
            xml_tree = self.record.get_latest_xml_tree()
            xml_text = self.record.get_latest_xml()
            choices_list = extract_bounds(xml_tree)
            image_path = self.page_executor.current_screenshot
            system_prompt = SeeActPrompts_xml.QUERY_SYSTEM_PROMPT
            query_user_prompt = SeeActPrompts_xml.QUERY_USER_PROMPT.format(
                task=self.instruction,
                previous_actions=("\n\n".join(self.stage_one_record) or "None"),
                xml_compressed=xml_text
            )
            query_message = {"role": "user", "content": query_user_prompt}

            referring_user_prompt = SeeActPrompts_xml.REFERRING_USER_PROMPT.format(
                option_prompt="\n".join(f"{item['key']} | {item['value']}" for item in choices_list)
            )

            messages = [
                {"role": "system", "content": system_prompt},
                query_message,
            ]

            # Stage 1. Query
            print(">> Stage 1. Query")
            with open("monitor.log", "w") as f:
                f.write(json.dumps(messages, indent=4))
            description = self.agent.act(messages)
            print(description, end="\n\n")
            with open("monitor.log", "w") as f:
                f.write(description)
            messages.append({"role": "assistant", "content": description})
            messages.append({"role": "user", "content": referring_user_prompt})

            # Stage 2. Referring
            print(">> Stage 2. Referring")
            with open("monitor.log", "w") as f:
                f.write(json.dumps(messages, indent=4))

            referring = self.agent.act(messages)
            print(referring, end="\n\n")
            with open("monitor.log", "w") as f:
                f.write(referring)


        except Exception as e:
            import traceback
            print(traceback.print_exc())
            # print_with_color(f"Error: {e}", "red")
            # exit(1)
        referring = referring.split("Final Answer:")[-1].strip()
        exe_res = self.page_executor(get_code_snippet(referring))
        self.stage_one_record.append(description)
        self.record.update_after(exe_res, description + "\n\n==========\n\n" + referring)
        self.record.turn_number += 1

class TextOnlyReactTask(TextOnlyTask):
    def set_system_prompt(self, instruction):
        self.record.history = [{
            "role": "system",
            "content": SYSTEM_PROMPT_ANDROID_TEXT_ReAct + f"\n\nTask Instruction: {instruction}"
        }]


class TextOnlyFineTuneTask(TextOnlyTask):
    def set_system_prompt(self, instruction):
        self.record.history = [{
            "role": "system",
            "content": SYSTEM_PROMPT_ANDROID_TEXT_GLM_v1_5 + f"\n\nTask Instruction: {instruction}"
        }]

    def run_step(self):
        self.record.update_before(controller=self.controller, need_screenshot=True, ac_status=self.accessibility)
        compressed_xml_json = self.record.get_latest_xml()
        round_count = self.record.get_round_count()

        # prompt = f"" if round_count == 0 else "** XML **\n"
        try:
            app_info = f"{json.dumps({'current_app': self.controller.get_current_app()}, ensure_ascii=False)}\n"
            current_message = {"role": "user", "content": app_info + compressed_xml_json}
            rsp = self.agent.act([*self.record.history, current_message])
        except Exception as e:
            print_with_color(f"Error: {e}", "red")

        exe_res = self.page_executor(get_code_snippet(rsp))
        self.record.update_after(exe_res, rsp)
        self.record.turn_number += 1


class TextOnlyFineTuneTask_long(TextOnlyFineTuneTask):
    def set_system_prompt(self, instruction):
        self.record.history = [{
            "role": "system",
            "content": SYSTEM_PROMPT_ANDROID_TEXT_GPT + f"\n\nTask Instruction: {instruction}"
        }]
