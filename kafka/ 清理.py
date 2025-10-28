#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from kafka import KafkaAdminClient, KafkaConsumer
from kafka.admin import NewTopic
from kafka.errors import KafkaError, GroupAuthorizationError, GroupIdNotFoundException
import time
import sys
import logging
from datetime import datetime, timedelta

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('kafka_cleanup')

def cleanup_stale_consumer_groups(bootstrap_servers, max_idle_hours=1):
    """
    清理超过指定小时无活动的消费者组
    :param bootstrap_servers: Kafka 服务器地址（例如 "localhost:9092"）
    :param max_idle_hours: 最大允许空闲时间（小时）
    """
    # 创建 Kafka Admin Client
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    
    # 创建 Consumer 来访问 __consumer_offsets
    consumer = KafkaConsumer(
        group_id='kafka-cleanup-tool',
        bootstrap_servers=bootstrap_servers,
        enable_auto_commit=False,
        auto_offset_reset='earliest',
        # 禁用主题自动发现以提高性能
        metadata_max_age_ms=30000
    )
    
    # 计算时间阈值（毫秒）
    threshold_ms = int((datetime.now() - timedelta(hours=max_idle_hours)).timestamp() * 1000)
    
    # 获取所有消费者组
    try:
        groups = admin_client.list_consumer_groups()
        group_ids = [group[0] for group in groups]
    except Exception as e:
        logger.error(f"Failed to list consumer groups: {str(e)}")
        return
    
    stale_groups = []
    active_groups = []
    
    # 检查每个消费者组的最后提交时间
    for group_id in group_ids:
        try:
            # 获取消费者组的元数据
            group_metadata = admin_client.describe_consumer_groups([group_id])[0]
            
            # 跳过有活跃成员的组
            if group_metadata.state == 'Stable' and group_metadata.members:
                active_groups.append(group_id)
                logger.debug(f"Group {group_id} is active, skipping")
                continue
            
            # 检查消费组的最新提交时间
            last_commit_time = None
            # 查询内部主题 __consumer_offsets 的分区信息
            for tp in consumer.partitions_for_topic('__consumer_offsets') or []:
                try:
                    # 获取消费者组对应的最新偏移量和时间戳
                    offsets = consumer.offsets_for_times({tp: threshold_ms})
                    if offsets and offsets.get(tp):
                        _, high_offset = consumer.get_watermark_offsets(tp)
                        # 检查消费者组在该分区上的提交情况
                        if group_id.encode('utf-8') in consumer.committed(tp) and consumer.committed(tp)[group_id.encode('utf-8')] >= high_offset:
                            last_commit_time = max(last_commit_time, offsets[tp].timestamp) if last_commit_time else offsets[tp].timestamp
                except (KafkaError, GroupAuthorizationError, GroupIdNotFoundException) as e:
                    logger.warning(f"Failed to check group {group_id} on partition {tp}: {str(e)}")
                    continue
            
            # 判断是否需要清理
            if not last_commit_time or last_commit_time < threshold_ms:
                stale_groups.append(group_id)
                logger.info(f"Group {group_id} is stale. Last commit: {datetime.fromtimestamp(last_commit_time/1000)}")
            else:
                logger.debug(f"Group {group_id} has recent activity")
                
        except Exception as e:
            logger.error(f"Error processing group {group_id}: {str(e)}")
    
    # 清理过时的消费者组
    if stale_groups:
        logger.info(f"Deleting stale consumer groups: {', '.join(stale_groups)}")
        try:
            admin_client.delete_consumer_groups(stale_groups)
            logger.info("Successfully deleted stale consumer groups")
        except Exception as e:
            logger.error(f"Failed to delete consumer groups: {str(e)}")
    else:
        logger.info("No stale consumer groups found")
    
    # 关闭连接
    consumer.close()
    admin_client.close()

if __name__ == "__main__":
  
    
    bootstrap_servers =  "bigdata01:9092"
    max_idle_hours =  1  # 默认为 1 小时
    
    try:
        logger.info(f"Starting cleanup process for bootstrap servers: {bootstrap_servers}")
        cleanup_stale_consumer_groups(bootstrap_servers, max_idle_hours)
        logger.info("Cleanup completed successfully")
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.exception(f"Critical error during cleanup: {str(e)}")
        sys.exit(1)




