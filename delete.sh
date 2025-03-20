#!/bin/bash

# 获取所有名为 python-android-env-test:latest 的容器 ID
container_ids=$(docker ps -a -q --filter ancestor=android_eval:v3)

# 停止并删除这些容器
if [ -n "$container_ids" ]; then
  echo "Stopping and removing containers..."
  
  # 并行停止容器
  for id in $container_ids; do
    docker stop $id &
  done

  # 等待所有停止操作完成
  wait

  # 并行删除容器
  for id in $container_ids; do
    docker rm $id &
  done

  # 等待所有删除操作完成
  wait
  
  echo "All specified containers have been stopped and removed."
else
  echo "No containers found for image python-android-env-test:latest."
fi

# 获取所有名为 python-android-env-test:latest 的容器 ID
container_ids=$(docker ps -a -q --filter ancestor=android_eval:aitw)

# 停止并删除这些容器
if [ -n "$container_ids" ]; then
  echo "Stopping and removing containers..."
  
  # 并行停止容器
  for id in $container_ids; do
    docker stop $id &
  done

  # 等待所有停止操作完成
  wait

  # 并行删除容器
  for id in $container_ids; do
    docker rm $id &
  done

  # 等待所有删除操作完成
  wait
  
  echo "All specified containers have been stopped and removed."
else
  echo "No containers found for image python-android-env-test:latest."
fi

# 获取所有名为 python-android-env-test:latest 的容器 ID
container_ids=$(docker ps -a -q --filter ancestor=android_eval:v2)

# 停止并删除这些容器
if [ -n "$container_ids" ]; then
  echo "Stopping and removing containers..."
  
  # 并行停止容器
  for id in $container_ids; do
    docker stop $id &
  done

  # 等待所有停止操作完成
  wait

  # 并行删除容器
  for id in $container_ids; do
    docker rm $id &
  done

  # 等待所有删除操作完成
  wait
  
  echo "All specified containers have been stopped and removed."
else
  echo "No containers found for image python-android-env-test:latest."
fi
