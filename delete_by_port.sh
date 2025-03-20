#!/bin/bash

# 获取端口范围内的所有容器ID
container_ids=$(docker ps --filter "publish=5000-5020" --format "{{.ID}}")

if [ -z "$container_ids" ]; then
    echo "没有找到匹配的容器。"
    exit 0
fi

# 并行停止容器
for id in $container_ids; do
    echo "正在停止容器 (ID: $id)..."
    docker stop $id &
done

# 等待所有停止操作完成
wait

# 并行删除容器
for id in $container_ids; do
    echo "正在删除容器 (ID: $id)..."
    docker rm $id &
done

# 等待所有删除操作完成
wait
