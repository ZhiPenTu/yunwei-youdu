#!/bin/bash
BOOTSTRAP_SERVERS="bigdata02:9092"
THRESHOLD_HOURS=1

# 获取所有消费者组
groups=$(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVERS --list)

# 循环检查每个组
for group in $groups; do
  # 获取最后提交时间
  last_commit=$(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVERS \
              --group $group --describe | grep 'last-commit' | awk '{print $NF}')
  
  # 检查时间差
  if [ -n "$last_commit" ]; then
    current_time=$(date +%s)
    hours_diff=$(( (current_time - last_commit) / 3600 ))
    
    # 删除超过阈值的组
    if [ $hours_diff -ge $THRESHOLD_HOURS ]; then
      echo "Deleting dead group: $group (last commit ${hours_diff} hours ago)"
      kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVERS \
        --delete --group $group
    fi
  fi
done

kafka-consumer-groups.sh --bootstrap-server bigdata02:9092 --list
kafka-consumer-groups.sh --bootstrap-server bigdata02:9092 --group 01f66827504a44f797b749331c3e1c49 --describe | grep 'last-commit' | awk '{print $NF}'
kafka-consumer-groups.sh --bootstrap-server bigdata02:9092 --delete --group 01f66827504a44f797b749331c3e1c49
kafka-consumer-groups.sh --bootstrap-server bigdata02:9092 --delete --group f43650ab334b477ea8c020fd5fd21c87
kafka-consumer-groups.sh --bootstrap-server bigdata02:9092 --delete --group 7fbe76d2239f42cdaa3672759ba44521

kafka-consumer-groups.sh --bootstrap-server bigdata02:9092 --delete --group d3aa5914e22a4123b72a375b5c5e3982
 --bootstrap-server bigdata02:9092 --delete --group 01f66827504a44f797b749331c3e1c49