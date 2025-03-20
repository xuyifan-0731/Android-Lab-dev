start=1
end=20

# 循环执行命令
for (( num=$start; num<=$end; num++ ))
do
    python eval.py -n lama3.1-8b-v26-xmlv2-full-3e-r${num}-temperature-1.0 -c /raid/xuyifan/Android-Lab-main/configs/llama-3.1-8-v26-sample.yaml -p 15
    #bash delete.sh
done

python generate_result.py

