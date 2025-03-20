from flask import Flask, request, jsonify
import subprocess
import threading
import os
import re   
from typing import Optional

app = Flask(__name__)

class EvalService:
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False

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

    def execute_eval(self, model_name: str, yaml_path: str, parrallel: int = 10):
        """执行 eval.py 的模型评估"""
        if self.is_running:
            return "任务已经在运行中"

        # 构建命令并启动子进程
        command = ["/raid/xuyifan/miniconda3/envs/agent/bin/python", "eval.py", "-n", model_name, "-c", yaml_path, "-p", str(parrallel)]
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
            os.system("bash /raid/xuyifan/Android-Lab-main/delete.sh")


    def is_eval_running(self):
        """检查 eval.py 是否仍在执行"""
        return self.is_running

# 实例化服务
eval_service = EvalService()

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
    yaml_path = data.get('yaml_path')
    parallel = data.get('parallel', 10)

    if not model_name or not yaml_path:
        return jsonify({"error": "请提供model_name和yaml_path参数"}), 400

    result = eval_service.execute_eval(model_name, yaml_path, parallel)
    return jsonify({"message": result})

@app.route('/check_status', methods=['GET'])
def check_status():
    """检查评估任务是否正在运行"""
    status = eval_service.is_eval_running()
    return jsonify({"is_running": status})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
