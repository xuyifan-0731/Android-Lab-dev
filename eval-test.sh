conda activate agent-android_world
#python eval.py -n en-v2_6_v4_nolaunch_1history-reasoning-round1-0304-full-4e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 15
#python eval.py -n en-v2_6_v4_nolaunch_1history-reasoning-round1-0304-continue-full-3e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl-2.yaml -p 15
python eval-androidworld.py -n v26_android_world_250307_1history-3e-fix -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 15
python eval-androidworld.py -n v26_android_world_250307_1history-3e-fix-2 -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 15
#python eval-androidworld.py -n en-v2_6_v4_nolaunch_1history-reasoning-round1-continue-full-3e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 15

#python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx


python eval-androidworld.py -n v26_android_world_250307_text__1history-3e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 15 && python eval.py -n v26_android_world_250307_text_1history-3e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx


python eval.py -n v26_android_world_250319_1history_aw_train_sample-0328-text-3e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx

python eval.py -n v26_android_world_250319_1history_aw_train_sample-0328-text-3e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx

python eval-androidworld.py -n v26_android_world_250312_1history-3e-packing -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 15 && python eval.py -n v26_android_world_250312_1history-3e-packing -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl-2.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx

python eval-androidworld.py -n v26_android_world_250312_1history-3e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 15 && python eval-androidworld.py -n v26_android_world_250312_1history-4e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 15 && python eval-androidworld.py -n v26_android_world_250312_text_1history-3e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-3.yaml -p 15


python eval-androidworld.py -n v26_android_world_250312_1history-3e-launch -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 15  && python eval.py -n v26_android_world_250312_1history-3e-launch -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx

python eval-androidworld.py -n v26subset_aw_train_sample-0317_from_0312_launch_3e-1e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 15  && python eval.py -n 26subset_aw_train_sample-0317_from_0312_launch_3e-1e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl-2.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx

python eval-androidworld.py -n v26_android_world_250312_1history_launch_filter300 -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 15  && python eval.py -n  v26_android_world_250312_1history_launch_filter300 -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 15

python eval-androidworld.py -n 0312_launch_3e_awr_subset_5e-7-1e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-3.yaml -p 15 --parallel_start_num 50 && python eval.py -n  0312_launch_3e_awr_subset_5e-7-1e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl-3.yaml -p 15 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx

python eval-androidworld.py -n aw_train_sample-0317_from_0312_launch_3e-1e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 15

python eval-androidworld.py -n v26_android_world_250319_1history_launch_filter300_aw_train_sample-0317-3e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 10 --parallel_start_num 20 && python eval.py -n  v26_android_world_250319_text_1history_launch_filter300_aw_train_sample-0317-3e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl.yaml -p 10 && python generate_result.py  --input_folder /raid/xuyifan/Android-Lab-main/logs/shudan --output_folder /raid/xuyifan/Android-Lab-main/outputs-qw --output_excel /raid/xuyifan/Android-Lab-main/output-qw.xlsx


python eval-androidworld.py -n v26_android_world_250319_1history_launch_filter300_aw_train_sample-0324-full -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 20 --parallel_start_num 20 

python eval-androidworld.py -n v26_android_world_250322_1history_launch_filter300_aw_train_sample-0324-full -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-1.yaml -p 20 --parallel_start_num 40

python eval.py -n  v26_android_world_250319_1history_launch_filter300_aw_train_sample-0317_rewrite1-3e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl-3.yaml -p 20

python eval-androidworld.py -n v26_android_world_250319_1history_aw_train_sample-0327_text-3e-text -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 20 --parallel_start_num 160 && python eval-androidworld.py -n v26_android_world_250319_1history_launch_filter300_aw_train_sample-0325-full-new-no-text -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-1.yaml -p 20 --parallel_start_num 20 && python eval-androidworld.py -n v26_android_world_250319_1history_launch_filter300_aw_train_sample-0325-full-new-4e-no-text -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 20 --parallel_start_num 40


python eval.py -n  v26_android_world_250319_1history_launch_filter300_aw_train_sample-0325-full-3e -c /raid/xuyifan/Android-Lab-main/configs/qwen25-vl-2.yaml -p 20

python eval-androidworld.py -n v26_android_world_250319_1history_launch_filter300_aw_train_sample-0325-full-2e-32b -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-32b.yaml -p 20 --parallel_start_num 80

python eval-androidworld.py -n v26_android_world_250319_1history_aw_train_sample-0328-text -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen.yaml -p 20 --parallel_start_num 160  && python eval-androidworld.py -n v26_android_world_250325_1history_aw_train_sample-0328-text -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 20 --parallel_start_num 40

python eval-androidworld.py -n v26_android_world_250319_1history_aw_train_sample-0329-text -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-1.yaml -p 20 --parallel_start_num 160 && python eval-androidworld.py -n v26_android_world_250319_1history_aw_train_sample-0329-text-4e -c /raid/xuyifan/Android-Lab-main/configs/android-world-qwen-2.yaml -p 20 --parallel_start_num 100