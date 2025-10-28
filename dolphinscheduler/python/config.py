#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块 - SeaTunnel数据同步任务

用于管理数据库连接信息、任务参数和DolphinScheduler工作流配置
支持环境变量配置，提高安全性和灵活性
"""

import os
from typing import Dict, Any, Optional

# 尝试加载dotenv，如果不存在则跳过
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed, using system environment variables only")


class Config:
    """配置管理类"""
    
    # MySQL数据库配置
    MYSQL_CONFIG = {
        'host': os.getenv('MYSQL_HOST', '192.168.1.100'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'database': os.getenv('MYSQL_DATABASE', 'test_db'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', '123456'),
        'charset': os.getenv('MYSQL_CHARSET', 'utf8mb4'),
        'autocommit': True,
        'cursorclass': 'DictCursor'  # 返回字典格式结果
    }
    
    # Doris数据库配置
    DORIS_CONFIG = {
        'fe_nodes': os.getenv('DORIS_FE_NODES', '192.168.1.101:8030').split(','),
        'username': os.getenv('DORIS_USERNAME', 'root'),
        'password': os.getenv('DORIS_PASSWORD', ''),
        'database': os.getenv('DORIS_DATABASE', 'test_db'),
        'table': os.getenv('DORIS_TABLE', 'ods_traffic_flow_statistics_1h'),
        'stream_load_format': os.getenv('DORIS_FORMAT', 'json'),
        'timeout': int(os.getenv('DORIS_TIMEOUT', 30)),
        'max_filter_ratio': float(os.getenv('DORIS_MAX_FILTER_RATIO', 0.1)),
        'label_prefix': os.getenv('DORIS_LABEL_PREFIX', 'seatunnel_task')
    }
    
    # 字段映射配置
    FIELD_MAPPING = {
        'id': 'id',
        'biz_time': 'biz_time',
        'section_id': 'section_id',
        'direction': 'direction',
        'device_no': 'device_no',
        'cycle': 'cycle',
        'lane_no': 'lane_no',
        'lane_type': 'lane_type',
        'vehicle_nums': 'vehicle_nums',
        'avg_speed': 'avg_speed',
        'avg_time': 'avg_time',
        'queue_len': 'queue_len',
        'create_time': 'create_time',
        'update_time': 'update_time',
        'del_flag': 'del_flag',
        'scene_type': 'scene_type'
    }
    
    # 任务配置
    TASK_CONFIG = {
        'batch_size': int(os.getenv('TASK_BATCH_SIZE', 1000)),
        'max_retries': int(os.getenv('TASK_MAX_RETRIES', 3)),
        'retry_delay': int(os.getenv('TASK_RETRY_DELAY', 5)),
        'timeout': int(os.getenv('TASK_TIMEOUT', 300)),
        'log_level': os.getenv('TASK_LOG_LEVEL', 'INFO'),
        'log_file': os.getenv('TASK_LOG_FILE', 'seatunnel_task.log'),
        'enable_metrics': os.getenv('TASK_ENABLE_METRICS', 'true').lower() == 'true'
    }
    
    # DolphinScheduler工作流配置
    WORKFLOW_CONFIG = {
        'name': os.getenv('WORKFLOW_NAME', 'seatunnel_to_doris_sync'),
        'description': os.getenv('WORKFLOW_DESCRIPTION', 'SeaTunnel数据同步到Doris'),
        'schedule': os.getenv('WORKFLOW_SCHEDULE', '0 */1 * * *'),  # 每小时执行
        'timezone': os.getenv('WORKFLOW_TIMEZONE', 'Asia/Shanghai'),
        'worker_group': os.getenv('WORKFLOW_WORKER_GROUP', 'default'),
        'tenant': os.getenv('WORKFLOW_TENANT', 'default'),
        'queue': os.getenv('WORKFLOW_QUEUE', 'default'),
        'release_state': os.getenv('WORKFLOW_RELEASE_STATE', 'ONLINE'),
        'execution_type': os.getenv('WORKFLOW_EXECUTION_TYPE', 'PARALLEL')
    }
    
    # DolphinScheduler连接配置
    DOLPHIN_CONFIG = {
        'host': os.getenv('DOLPHIN_HOST', 'localhost'),
        'port': int(os.getenv('DOLPHIN_PORT', 12345)),
        'username': os.getenv('DOLPHIN_USERNAME', 'admin'),
        'password': os.getenv('DOLPHIN_PASSWORD', 'dolphinscheduler123'),
        'project_name': os.getenv('DOLPHIN_PROJECT', 'seatunnel_project')
    }
    
    @classmethod
    def get_mysql_config(cls) -> Dict[str, Any]:
        """获取MySQL配置"""
        return cls.MYSQL_CONFIG.copy()
    
    @classmethod
    def get_doris_config(cls) -> Dict[str, Any]:
        """获取Doris配置"""
        return cls.DORIS_CONFIG.copy()
    
    @classmethod
    def get_field_mapping(cls) -> Dict[str, str]:
        """获取字段映射配置"""
        return cls.FIELD_MAPPING.copy()
    
    @classmethod
    def get_task_config(cls) -> Dict[str, Any]:
        """获取任务配置"""
        return cls.TASK_CONFIG.copy()
    
    @classmethod
    def get_workflow_config(cls) -> Dict[str, Any]:
        """获取工作流配置"""
        return cls.WORKFLOW_CONFIG.copy()
    
    @classmethod
    def get_dolphin_config(cls) -> Dict[str, Any]:
        """获取DolphinScheduler配置"""
        return cls.DOLPHIN_CONFIG.copy()
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置有效性"""
        try:
            # 验证MySQL配置
            mysql_config = cls.get_mysql_config()
            required_mysql_keys = ['host', 'port', 'database', 'user', 'password']
            for key in required_mysql_keys:
                if not mysql_config.get(key):
                    print(f"MySQL配置缺少必需参数: {key}")
                    return False
            
            # 验证Doris配置
            doris_config = cls.get_doris_config()
            required_doris_keys = ['fe_nodes', 'username', 'database', 'table']
            for key in required_doris_keys:
                if not doris_config.get(key):
                    print(f"Doris配置缺少必需参数: {key}")
                    return False
            
            # 验证端口号
            if not (1 <= mysql_config['port'] <= 65535):
                print(f"MySQL端口号无效: {mysql_config['port']}")
                return False
            
            # 验证批处理大小
            task_config = cls.get_task_config()
            if task_config['batch_size'] <= 0:
                print(f"批处理大小无效: {task_config['batch_size']}")
                return False
            
            # 验证重试次数
            if task_config['max_retries'] < 0:
                print(f"最大重试次数无效: {task_config['max_retries']}")
                return False
            
            print("配置验证通过")
            return True
            
        except Exception as e:
            print(f"配置验证失败: {str(e)}")
            return False
    
    @classmethod
    def get_mysql_connection_string(cls) -> str:
        """获取MySQL连接字符串（用于日志显示，不包含密码）"""
        config = cls.get_mysql_config()
        return f"mysql://{config['user']}@{config['host']}:{config['port']}/{config['database']}"
    
    @classmethod
    def get_doris_connection_string(cls) -> str:
        """获取Doris连接字符串（用于日志显示，不包含密码）"""
        config = cls.get_doris_config()
        fe_nodes = ','.join(config['fe_nodes'])
        return f"doris://{config['username']}@{fe_nodes}/{config['database']}.{config['table']}"
    
    @classmethod
    def print_config_summary(cls) -> None:
        """打印配置摘要"""
        print("=" * 50)
        print("配置摘要")
        print("=" * 50)
        
        print(f"MySQL连接: {cls.get_mysql_connection_string()}")
        print(f"Doris连接: {cls.get_doris_connection_string()}")
        
        task_config = cls.get_task_config()
        print(f"批处理大小: {task_config['batch_size']}")
        print(f"最大重试次数: {task_config['max_retries']}")
        print(f"日志级别: {task_config['log_level']}")
        
        workflow_config = cls.get_workflow_config()
        print(f"工作流名称: {workflow_config['name']}")
        print(f"调度表达式: {workflow_config['schedule']}")
        print(f"时区: {workflow_config['timezone']}")
        
        print("=" * 50)


# 环境变量配置示例
ENV_EXAMPLE = """
# MySQL数据库配置
MYSQL_HOST=192.168.1.100
MYSQL_PORT=3306
MYSQL_DATABASE=test_db
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_CHARSET=utf8mb4

# Doris数据库配置
DORIS_FE_NODES=192.168.1.101:8030,192.168.1.102:8030
DORIS_USERNAME=root
DORIS_PASSWORD=
DORIS_DATABASE=test_db
DORIS_TABLE=ods_traffic_flow_statistics_1h
DORIS_FORMAT=json
DORIS_TIMEOUT=30
DORIS_MAX_FILTER_RATIO=0.1

# 任务执行配置
TASK_BATCH_SIZE=1000
TASK_MAX_RETRIES=3
TASK_RETRY_DELAY=5
TASK_TIMEOUT=300
TASK_LOG_LEVEL=INFO
TASK_ENABLE_METRICS=true

# DolphinScheduler工作流配置
WORKFLOW_NAME=seatunnel_to_doris_sync
WORKFLOW_DESCRIPTION=SeaTunnel数据同步到Doris
WORKFLOW_SCHEDULE=0 */1 * * *
WORKFLOW_TIMEZONE=Asia/Shanghai
WORKFLOW_WORKER_GROUP=default
WORKFLOW_TENANT=default
WORKFLOW_QUEUE=default
WORKFLOW_RELEASE_STATE=ONLINE
WORKFLOW_EXECUTION_TYPE=PARALLEL

# DolphinScheduler连接配置
DOLPHIN_HOST=localhost
DOLPHIN_PORT=12345
DOLPHIN_USERNAME=admin
DOLPHIN_PASSWORD=dolphinscheduler123
DOLPHIN_PROJECT=seatunnel_project
"""


if __name__ == '__main__':
    # 测试配置
    print("测试配置模块...")
    
    # 打印配置摘要
    Config.print_config_summary()
    
    # 验证配置
    if Config.validate_config():
        print("\n✅ 配置验证通过")
    else:
        print("\n❌ 配置验证失败")
    
    # 显示环境变量示例
    print("\n环境变量配置示例:")
    print(ENV_EXAMPLE)