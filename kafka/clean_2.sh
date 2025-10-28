#!/bin/bash
# 修复版的Kafka消费者组清理脚本
BOOTSTRAP_SERVERS="bigdata02:9092"
THRESHOLD_HOURS=1

# 获取所有消费者组
groups=$(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVERS --list 2>/dev/null)

echo "发现消费者组数量: $(echo "$groups" | wc -l)"

# 循环检查每个组
for group in $groups; do
  # 跳过内部组
  if [[ $group == __* ]]; then
    echo "跳过系统组: $group"
    continue
  fi
  
  # 获取组信息并忽略无活跃成员警告
  describe_output=$(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVERS \
                  --group $group --describe 2>&1)
  
  # 检查是否无活跃成员（这表示组是空的）
  if echo "$describe_output" | grep -q "has no active members"; then
    echo "检测到空组: $group (无活跃成员)"
    last_commit=""
  else
    last_commit=$(echo "$describe_output" | grep "last-commit" | awk '{print $NF}')
  fi
  
  # 处理无提交时间的情况
  if [ -z "$last_commit" ]; then
    echo "组 $group 没有提交时间信息 - 标记为挂死状态"
    should_delete=true
  else
    # 计算时间差（秒）
    current_time=$(date +%s)
    hours_diff=$(( (current_time - last_commit) / 3600 ))
    
    echo "组 $group: 最后提交 $hours_diff 小时前"
    
    if [ $hours_diff -ge $THRESHOLD_HOURS ]; then
      should_delete=true
    else
      should_delete=false
    fi
  fi
  
  # 删除挂死组
  if [ "$should_delete" = true ]; then
    echo "正在删除挂死组: $group"
    # 使用静默模式忽略成功信息
    kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVERS \
        --delete --group $group >/dev/null 2>&1
    
    # 检查是否删除成功
    if kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVERS \
        --describe --group $group 2>&1 | grep -q "Consumer group '$group' does not exist"; then
      echo "成功删除组: $group"
    else
      echo "删除组 $group 失败"
    fi
  fi
done

echo "清理操作完成"