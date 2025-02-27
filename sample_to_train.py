from flask import Flask, request, jsonify
import subprocess
import threading
import os
import re
import json   
import shutil
import zipfile
from io import BytesIO
from flask import send_file

import yaml
import tempfile
from typing import Optional

app = Flask(__name__)

class EvalService:
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.base_path = "/raid/xuyifan/Android-Lab-main"
        self.save_dir = None

    def check_free_memory(self):
        """使用free -h命令查询系统内存信息，并提取free值"""
        result = subprocess.run(["free", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            # 使用正则表达式提取Free的值
            match = re.search(r'Mem:\s+\S+\s+\S+\s+(\S+)', result.stdout)
            if match:
                free_memory = match.group(1)
                return f"{free_memory}"
            else:
                return "无法提取free内存值"
        else:
            return f"查询内存信息失败：{result.stderr}"

    def execute_eval(self, model_name: str, yaml_content, parallel: int = 1, sample_epoch = 3):
        """执行 eval.py 的模型评估"""
        if self.is_running:
            return "任务已经在运行中"

        # 提取保存路径
        save_dir = yaml_content.get('task', {}).get('args', {}).get('save_dir')
        if not save_dir:
            return jsonify({"error": "YAML文件中缺少task.args.save_dir参数"}), 400
        save_dir = os.path.join(self.base_path, save_dir)
        self.save_dir = save_dir
        print(f"保存路径: {save_dir}")
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存YAML文件
        yaml_file_path = os.path.join(save_dir, 'uploaded_eval_config.yaml')
        with open(yaml_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f)

        # 构建命令并启动子进程
        command = ["bash","/raid/xuyifan/pipeline-sample/pipeline-mobile/sample.sh",model_name, yaml_file_path, str(parallel),str(sample_epoch)]
      
        print(command)
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.is_running = True
        threading.Thread(target=self._monitor_process).start()  # 开启后台线程监控进程状态
        return "评估任务已启动"

    def _monitor_process(self):
        """监控 eval.py 的执行状态"""
        if self.process:
            stdout, stderr = self.process.communicate()  # 等待进程结束
            self.is_running = False  # 进程结束后重置运行状态
            # execute "bash /raid/xuyifan/Android-Lab-main/delete.sh"
            # os.system("bash /raid/xuyifan/pipeline-sample/pipeline-mobile/delete.sh")


    def is_eval_running(self):
        """检查 eval.py 是否仍在执行"""
        if not self.is_running:
            return self.is_running, "任务完成"
        if os.path.exists(os.path.join(self.save_dir, 'info.json')):
            with open(os.path.join(self.save_dir, 'info.json'), 'r') as f:
                info = json.load(f)
                epoch = info.get('epoch')
                now_epoch = info.get('now_epoch')
                task_num = info.get('task_num')
                now_log_path = os.path.join(self.save_dir,info.get('now_log_path'))
            print(now_log_path)
            if os.path.exists(now_log_path):
                task_num_run = len(os.listdir(now_log_path))
            else:
                task_num_run = 0
            return_info = f"Epoch {now_epoch}/{epoch}, {task_num_run}/{task_num} tasks have been subbmitted"
        else:
            return_info = "No start yet"
        return self.is_running, return_info

    def get_sample_logs(self, model_name: str, sample_epoch: int, need_pic: bool, load_log_path: str = None, save_log_path: str = None):
        if load_log_path:
            logs_path = load_log_path
        else:
            print("self.save_dir",self.save_dir)
            logs_path = self.save_dir
        if save_log_path:
            temp_dir = save_log_path
        else:
            temp_dir = "/tmp/sample_logs"
        os.makedirs(temp_dir, exist_ok=True)

        # 遍历所有的sample_epoch
        for num in range(1, sample_epoch + 1):
            folder_name = f"{model_name}_r{num}"
            print("logs_path",logs_path)
            print("folder_name",folder_name)

            folder_path = os.path.join(logs_path, folder_name)

            if not os.path.exists(folder_path):
                continue  # 如果文件夹不存在，跳过

            # 复制目录结构到临时目录
            for root, dirs, filenames in os.walk(folder_path):
                # 创建目标目录
                target_dir = os.path.join(temp_dir, os.path.relpath(root, logs_path))
                os.makedirs(target_dir, exist_ok=True)

                for filename in filenames:
                    file_path = os.path.join(root, filename)

                    # 如果需要非图片文件，且文件是图片格式则跳过
                    if not need_pic and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        continue

                    # 复制文件到临时目录
                    shutil.copy(file_path, os.path.join(target_dir, filename))

        return temp_dir  # 返回临时目录路径，稍后进行打包

    def zip_directory(self, dir_path: str):
        """将目录压缩为zip文件并返回为BytesIO对象"""
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 将文件添加到zip文件中，保持目录结构
                    zip_file.write(file_path, os.path.relpath(file_path, dir_path))
        zip_buffer.seek(0)  # 将指针移动到文件开头
        return zip_buffer

# 实例化服务
eval_service = EvalService()
app = Flask(__name__)

@app.route('/check_memory', methods=['GET'])
def check_memory():
    """检查系统内存"""
    memory_info = eval_service.check_free_memory()
    return jsonify({"memory_info": memory_info})



@app.route('/start_eval', methods=['POST'])
def start_eval():
    """启动评估任务"""
    data = request.json
    model_name = data.get('model_name')
    yaml_content = data.get('yaml_content')
    parallel = data.get('parallel', 1)
    epoch = data.get('epoch', 1)

    if not model_name or not yaml_content:
        return jsonify({"error": "请提供model_name和yaml_content参数"}), 400

    try:
        # 执行评估任务
        result = eval_service.execute_eval(model_name, yaml_content, parallel, epoch)
        return jsonify({"message": result})
    
    except Exception as e:
        return jsonify({"error": f"处理YAML文件时出错: {str(e)}"}), 500



@app.route('/check_status', methods=['GET'])
def check_status():
    """检查评估任务是否正在运行"""
    status, return_info = eval_service.is_eval_running()
    return jsonify({"is_running": status, "info": return_info})

@app.route('/get_sample_logs', methods=['GET'])
def get_sample_logs():
    """获取采样记录"""
    model_name = request.args.get('model_name')
    sample_epoch = int(request.args.get('sample_epoch', 3))  # 默认值为3
    need_pic = request.args.get('need_pic', 'false').lower() == 'true'  # 默认为False

    if not model_name:
        return jsonify({"error": "请提供model_name参数"}), 400

    # 获取采样日志文件夹并保持目录结构
    temp_dir = eval_service.get_sample_logs(model_name, sample_epoch, need_pic)

    # 将目录压缩为ZIP文件
    zip_buffer = eval_service.zip_directory(temp_dir)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    # 返回压缩文件作为响应
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name=f"{model_name}_logs.zip")

def get_sample_log_local(model_name: str, sample_epoch: int, need_pic: bool, load_log_path: str = None, save_log_path: str = None):
    """获取采样记录"""
    temp_dir = eval_service.get_sample_logs(model_name, sample_epoch, need_pic, load_log_path, save_log_path)
    return temp_dir


    
if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=8001)
    from sample_tools.format_train_data import format_sample, format_sample_reward_only
    task_name = "qwen25-vl-v26-mergev4-3e-sample-androidgen-452train"
    load_log_path = "/raid/xuyifan/Android-Lab-main/logs/android_world_sample"
    save_log_path = "/raid/xuyifan/Android-Lab-main/sample-tmp"
    #get_sample_log_local(task_name, 1, True, load_log_path, save_log_path)
    #format_sample(f"{save_log_path}", f"/raid/xuyifan/Android-Lab-main/sample_dump/{task_name}-format", add_combined_reward_model=True)
    format_sample_reward_only(f"{save_log_path}", f"/raid/xuyifan/Android-Lab-main/sample_dump/{task_name}-format", add_combined_reward_model=True)

