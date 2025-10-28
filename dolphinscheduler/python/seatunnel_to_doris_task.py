#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SeaTunnel数据同步任务 - DolphinScheduler版本

功能说明:
1. 从MySQL数据库读取iot_json表数据
2. 进行字段映射和数据转换
3. 将处理后的数据写入Doris数据库
4. 支持增量同步和全量同步
5. 包含完整的异常处理和日志记录

原始配置来源: SeaTunnel配置文件
转换为DolphinScheduler Python任务格式
"""

import logging
import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import time
import os

# 导入配置文件
try:
    from config import Config
except ImportError:
    print("配置文件导入失败，请确保config.py文件存在")
    sys.exit(1)

# 基础库导入
try:
    import pymysql
    import requests
except ImportError as e:
    print(f"导入依赖包失败: {e}")
    print("请运行: pip install pymysql requests")
    # 继续运行，不退出

# DolphinScheduler相关导入（可选）
try:
    from pydolphinscheduler import Workflow, Task
    from pydolphinscheduler.tasks import Python
    from pydolphinscheduler.core.task import task
    DOLPHIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: DolphinScheduler模块导入失败: {e}")
    print("将以独立模式运行，不使用DolphinScheduler调度功能")
    DOLPHIN_AVAILABLE = False
    
    # 定义一个简单的装饰器替代
    def task(task_id: str, **kwargs):
        def decorator(func):
            func.task_id = task_id
            return func
        return decorator


# 从配置文件获取配置信息
MYSQL_CONFIG = Config.get_mysql_config()
DORIS_CONFIG = Config.get_doris_config()
FIELD_MAPPING = Config.get_field_mapping()
TASK_CONFIG = Config.get_task_config()
WORKFLOW_CONFIG = Config.get_workflow_config()


def setup_logging() -> logging.Logger:
    """设置日志配置
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger('seatunnel_task')
    
    # 从配置获取日志级别
    log_level = getattr(logging, TASK_CONFIG['log_level'].upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # 创建文件处理器
    log_file = TASK_CONFIG['log_file']
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger


def get_mysql_connection():
    """获取MySQL数据库连接
    
    Returns:
        pymysql.Connection: MySQL数据库连接对象
    """
    logger = logging.getLogger('seatunnel_task')
    
    try:
        logger.info(f"正在连接MySQL数据库: {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}")
        connection = pymysql.connect(**MYSQL_CONFIG)
        logger.info("MySQL数据库连接成功")
        return connection
        
    except Exception as e:
        logger.error(f"连接MySQL数据库失败: {str(e)}")
        raise


def get_time_range() -> tuple:
    """获取数据同步的时间范围
    
    Returns:
        tuple: (start_time, end_time) 时间范围元组
    """
    logger = logging.getLogger('seatunnel_task')
    
    try:
        # 获取昨天的时间范围
        yesterday = datetime.now() - timedelta(days=1)
        start_time = yesterday.strftime('%Y-%m-%d 00:00:00')
        end_time = yesterday.strftime('%Y-%m-%d 23:59:59')
        
        logger.info(f"时间范围: {start_time} 到 {end_time}")
        return start_time, end_time
        
    except Exception as e:
        logger.error(f"获取时间范围失败: {str(e)}")
        raise
    
def extract_data_from_mysql(connection, 
                           start_time: str, 
                           end_time: str,
                           batch_size: Optional[int] = None) -> List[Dict[str, Any]]:
    """从MySQL提取数据
    
    Args:
        connection: MySQL数据库连接
        start_time: 开始时间
        end_time: 结束时间
        batch_size: 批次大小，如果为None则使用配置中的默认值
        
    Returns:
        List[Dict[str, Any]]: 提取的数据列表
    """
    logger = logging.getLogger('seatunnel_task')
    
    if batch_size is None:
        batch_size = TASK_CONFIG['batch_size']
    
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 构建查询SQL
            sql = """
            SELECT id, biz_time, section_id, direction, device_no, cycle,
                   lane_no, lane_type, vehicle_nums, avg_speed, avg_time,
                   queue_len, create_time, update_time, del_flag, scene_type
            FROM iot_json 
            WHERE create_time >= %s AND create_time < %s
            ORDER BY create_time
            LIMIT %s
            """
            
            logger.info(f"执行查询SQL: {sql}")
            logger.info(f"查询参数: start_time={start_time}, end_time={end_time}, batch_size={batch_size}")
            
            cursor.execute(sql, (start_time, end_time, batch_size))
            results = cursor.fetchall()
            
            logger.info(f"成功提取 {len(results)} 条记录")
            return results
            
    except Exception as e:
        logger.error(f"从MySQL提取数据失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise
    
def transform_data(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """数据转换和字段映射
    
    Args:
        raw_data: 原始数据列表
        
    Returns:
        List[Dict[str, Any]]: 转换后的数据列表
    """
    logger = logging.getLogger('seatunnel_task')
    
    try:
        transformed_data = []
        
        for record in raw_data:
            transformed_record = {}
            
            # 应用字段映射
            for source_field, target_field in FIELD_MAPPING.items():
                if source_field in record:
                    value = record[source_field]
                    # 处理datetime对象
                    if isinstance(value, datetime):
                        value = value.strftime('%Y-%m-%d %H:%M:%S')
                    transformed_record[target_field] = value
                else:
                    logger.warning(f"源字段 {source_field} 不存在于记录中")
                    transformed_record[target_field] = None
            
            transformed_data.append(transformed_record)
        
        logger.info(f"成功转换 {len(transformed_data)} 条记录")
        return transformed_data
        
    except Exception as e:
        logger.error(f"数据转换失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise
    
def load_data_to_doris(data: List[Dict[str, Any]], 
                       table_name: str = 'iot_json',
                       max_retries: Optional[int] = None) -> bool:
    """将数据加载到Doris
    
    Args:
        data: 要加载的数据
        table_name: 目标表名
        max_retries: 最大重试次数，如果为None则使用配置中的默认值
        
    Returns:
        bool: 是否加载成功
    """
    logger = logging.getLogger('seatunnel_task')
    
    # 检查requests模块是否可用
    try:
        import requests
    except ImportError:
        logger.error("requests模块不可用，无法加载数据到Doris")
        raise ImportError("requests模块未安装，请运行: pip install requests")
    
    if not data:
        logger.warning("没有数据需要加载到Doris")
        return True
    
    if max_retries is None:
        max_retries = TASK_CONFIG['max_retries']
    
    # 构建Stream Load URL
    fe_node = DORIS_CONFIG['fe_nodes']
    database = DORIS_CONFIG['database']
    url = f"http://{fe_node}/api/{database}/{table_name}/_stream_load"
    
    # 生成唯一标签
    label = f"{DORIS_CONFIG['label_prefix']}_{int(time.time() * 1000)}"
    
    # 准备请求头
    headers = {
        'label': label,
        'format': DORIS_CONFIG['stream_load_format'],
        'read_json_by_line': 'true',
        'enable_2pc': 'false'
    }
    
    # 准备认证信息
    auth = (DORIS_CONFIG['username'], DORIS_CONFIG['password'])
    
    # 准备数据
    json_data = '\n'.join([json.dumps(record, ensure_ascii=False, default=str) for record in data])
    
    # 重试机制
    retry_delay = TASK_CONFIG['retry_delay']
    timeout = DORIS_CONFIG.get('timeout', 300)
    
    for attempt in range(max_retries):
        try:
            logger.info(f"开始向Doris加载数据，尝试次数: {attempt + 1}/{max_retries}")
            logger.info(f"URL: {url}")
            logger.info(f"Label: {label}")
            logger.info(f"数据条数: {len(data)}")
            
            response = requests.put(
                url=url,
                headers=headers,
                auth=auth,
                data=json_data.encode('utf-8'),
                timeout=timeout
            )
            
            logger.info(f"Doris响应状态码: {response.status_code}")
            logger.info(f"Doris响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('Status') == 'Success':
                    logger.info(f"数据成功加载到Doris，加载条数: {result.get('NumberLoadedRows', 0)}")
                    return True
                else:
                    logger.error(f"Doris加载失败: {result.get('Message', '未知错误')}")
            else:
                logger.error(f"HTTP请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            logger.error(f"向Doris加载数据失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            
            if attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)  # 递增等待时间
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
    
    logger.error(f"经过 {max_retries} 次尝试后，数据加载到Doris仍然失败")
    return False
    
def main_etl_process() -> bool:
    """主要的ETL处理流程
    
    Returns:
        bool: 处理是否成功
    """
    logger = logging.getLogger('seatunnel_task')
    connection = None
    
    try:
        logger.info("开始执行ETL流程")
        
        # 1. 获取时间范围
        start_time, end_time = get_time_range()
        
        # 2. 连接MySQL数据库
        connection = get_mysql_connection()
        
        # 3. 从MySQL提取数据
        raw_data = extract_data_from_mysql(connection, start_time, end_time)
        
        if not raw_data:
            logger.info("没有需要同步的数据")
            return True
        
        # 4. 数据转换
        transformed_data = transform_data(raw_data)
        
        # 5. 加载数据到Doris
        success = load_data_to_doris(transformed_data)
        
        if success:
            logger.info(f"ETL流程执行成功，共处理 {len(transformed_data)} 条记录")
            return True
        else:
            logger.error("ETL流程执行失败")
            return False
            
    except Exception as e:
        logger.error(f"ETL流程执行过程中发生异常: {str(e)}")
        logger.error(f"异常详情: {traceback.format_exc()}")
        return False
        
    finally:
        if connection:
            connection.close()
            logger.info("MySQL连接已关闭")
    
def create_workflow():
    """创建DolphinScheduler工作流（如果可用）"""
    logger = logging.getLogger('seatunnel_task')
    
    if not DOLPHIN_AVAILABLE:
        logger.info("DolphinScheduler不可用，跳过工作流创建")
        return None
    
    try:
        # 从配置获取工作流参数
        workflow_config = WORKFLOW_CONFIG
        
        # 创建工作流
        with Workflow(
            name=workflow_config['name'],
            schedule=workflow_config['schedule'],
            start_time=workflow_config['start_time'],
            tenant=workflow_config['tenant'],
            timeout=workflow_config['timeout'],
            warning_type=workflow_config['warning_type'],
            execution_type=workflow_config['execution_type']
        ) as workflow:
            
            # 创建Python任务
            task = Python(
                name="mysql_to_doris_etl",
                code=main_etl_process,
                timeout=workflow_config['timeout']
            )
            
        logger.info(f"工作流 '{workflow_config['name']}' 创建成功")
        logger.info(f"调度配置: {workflow_config['schedule']}")
        return workflow
        
    except Exception as e:
        logger.error(f"创建工作流失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise
    
if __name__ == "__main__":
    # 验证配置
    if not Config.validate_config():
        print("❌ 配置验证失败，请检查配置文件")
        sys.exit(1)
    
    # 设置日志
    logger = setup_logging()
    
    try:
        logger.info("开始执行SeaTunnel数据同步任务")
        logger.info(f"任务配置: {TASK_CONFIG}")
        logger.info(f"MySQL配置: {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}")
        logger.info(f"Doris配置: {DORIS_CONFIG['fe_nodes']}/{DORIS_CONFIG['database']}")
        
        # 执行主要的ETL流程
        success = main_etl_process()
        
        if success:
            logger.info("✅ SeaTunnel数据同步任务执行成功")
            sys.exit(0)
        else:
            logger.error("❌ SeaTunnel数据同步任务执行失败")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"任务执行过程中发生未预期的错误: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        sys.exit(1)