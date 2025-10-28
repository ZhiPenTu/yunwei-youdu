#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本 - 验证基本功能
不依赖外部包，只使用Python标准库
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('simple_test')

def test_config_loading():
    """测试配置文件加载"""
    try:
        import config
        logger.info("✓ 配置模块加载成功")
        
        # 测试配置获取
        mysql_config = config.Config.get_mysql_config()
        logger.info(f"✓ MySQL配置获取成功: {mysql_config['host']}:{mysql_config['port']}")
        
        doris_config = config.Config.get_doris_config()
        logger.info(f"✓ Doris配置获取成功: {doris_config['fe_nodes'][0]}")
        
        return True
    except Exception as e:
        logger.error(f"✗ 配置测试失败: {e}")
        return False

def test_main_script_import():
    """测试主脚本导入"""
    try:
        import seatunnel_to_doris_task
        logger.info("✓ 主脚本导入成功")
        
        # 测试时间范围获取函数
        start_time, end_time = seatunnel_to_doris_task.get_time_range()
        logger.info(f"✓ 时间范围获取成功: {start_time} - {end_time}")
        
        return True
    except Exception as e:
        logger.error(f"✗ 主脚本测试失败: {e}")
        return False

def test_time_functions():
    """测试时间处理函数"""
    try:
        # 测试时间格式化
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        start_time = yesterday.strftime('%Y-%m-%d %H:%M:%S')
        end_time = now.strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"✓ 时间处理测试成功: {start_time} - {end_time}")
        return True
    except Exception as e:
        logger.error(f"✗ 时间处理测试失败: {e}")
        return False

def test_field_mapping():
    """测试字段映射配置"""
    try:
        import config
        
        # 测试字段映射获取
        field_mapping = config.Config.get_field_mapping()
        logger.info(f"✓ 字段映射获取成功，包含 {len(field_mapping)} 个字段")
        
        # 检查关键字段
        required_fields = ['id', 'biz_time', 'create_time']
        for field in required_fields:
            if field in field_mapping:
                logger.info(f"  ✓ 关键字段 '{field}' 存在")
            else:
                logger.warning(f"  ⚠️ 关键字段 '{field}' 缺失")
        
        return True
    except Exception as e:
        logger.error(f"✗ 字段映射测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    logger.info("开始运行简单测试...")
    logger.info("=" * 50)
    
    tests = [
        ("配置加载测试", test_config_loading),
        ("主脚本导入测试", test_main_script_import),
        ("时间处理测试", test_time_functions),
        ("字段映射测试", test_field_mapping),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n运行 {test_name}...")
        if test_func():
            passed += 1
        else:
            logger.error(f"{test_name} 失败")
    
    logger.info("=" * 50)
    logger.info(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！")
        return 0
    else:
        logger.warning(f"⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())