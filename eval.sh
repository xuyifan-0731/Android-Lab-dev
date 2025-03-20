#python eval.py -n som-gpt-4o-mini-2024-07-18 -c /raid/xuyifan/Android-Lab-main/configs/public-test/xml-4omini.yaml -p 5
#bash /raid/xuyifan/Android-Lab-main/delete.sh
#python eval.py -n som-gpt-4-turbo-2024-04-09 -c /raid/xuyifan/Android-Lab-main/configs/public-test/xml-4o-turbo.yaml -p 5
#bash /raid/xuyifan/Android-Lab-main/delete.sh
#python eval.py -n som-gpt-4o-2024-08-06 -c /raid/xuyifan/Android-Lab-main/configs/public-test/xml-4o-08.yaml -p 5
#bash /raid/xuyifan/Android-Lab-main/delete.sh
python eval.py -n som-seeact-gpt-4o-2024-05-13 -c /raid/xuyifan/Android-Lab-main/configs/public-test/som-4o-05-seeact.yaml -p 10
bash /raid/xuyifan/Android-Lab-main/delete.sh
python eval.py -n xml-seeact-gpt-4o-2024-05-13 -c /raid/xuyifan/Android-Lab-main/configs/public-test/xml-4o-05-seeact.yaml -p 10
bash /raid/xuyifan/Android-Lab-main/delete.sh
python generate_result.py