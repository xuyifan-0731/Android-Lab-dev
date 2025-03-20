#将 /raid/xuyifan/Android-Lab-main/logs/shudan 下以v26_android_world_250312_1history-3e-launch开头的文件夹复制到 /raid/xuyifan/Android-Lab-main/sample_test 下
import os
import shutil

source_dir = "/raid/xuyifan/Android-Lab-main/logs/shudan"
target_dir = "/raid/xuyifan/Android-Lab-main/sample_test"

for file in os.listdir(source_dir):
    if file.startswith("v26_android_world_250312_1history-3e-launch"):
        shutil.copytree(os.path.join(source_dir, file), os.path.join(target_dir, file))
