conda activate agent-android_world
#python eval.py -n en-v2_6_v4_nolaunch_1history-reasoning-round1-0304-full-4e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 15
#python eval.py -n en-v2_6_v4_nolaunch_1history-reasoning-round1-0304-continue-full-3e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl-2.yaml -p 15
python eval-androidworld.py -n v26_android_world_250307_1history-3e-fix -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 15
python eval-androidworld.py -n v26_android_world_250307_1history-3e-fix-2 -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 15
#python eval-androidworld.py -n en-v2_6_v4_nolaunch_1history-reasoning-round1-continue-full-3e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 15

#python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx


python eval-androidworld.py -n v26_android_world_250307_text__1history-3e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 15 && python eval.py -n v26_android_world_250307_text_1history-3e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx


python eval.py -n v26_android_world_250307_1history-from-2196-3e-fix -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx

python eval.py -n v26_android_world_250307_text_1history-4e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx

python eval-androidworld.py -n v26_android_world_250312_1history-3e-packing -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 15 && python eval.py -n v26_android_world_250312_1history-3e-packing -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl-2.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx

python eval-androidworld.py -n v26_android_world_250312_1history-3e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 15 && python eval-androidworld.py -n v26_android_world_250312_1history-4e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 15 && python eval-androidworld.py -n v26_android_world_250312_text_1history-3e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-3.yaml -p 15


python eval-androidworld.py -n v26_android_world_250312_1history-3e-launch -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 15  && python eval.py -n v26_android_world_250312_1history-3e-launch -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx

python eval-androidworld.py -n v26_android_world_250312_1history-3e-launch-add-subsetsft-2e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 15  && python eval.py -n v26_android_world_250312_1history-3e-launch-add-subsetsft-2e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx