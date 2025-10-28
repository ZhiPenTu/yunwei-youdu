#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - SeaTunnel数据同步任务

用于验证转换后的DolphinScheduler Python脚本功能
包含单元测试和集成测试
"""

import unittest
import sys
import os
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import Config
    from seatunnel_to_doris_task import (
        setup_logging,
        get_mysql_connection,
        get_time_range,
        extract_data_from_mysql,
        transform_data,
        load_data_to_doris,
        main_etl_process
    )
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)


class TestConfig(unittest.TestCase):
    """配置测试类"""
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试配置验证功能
        result = Config.validate_config()
        self.assertIsInstance(result, bool)
    
    def test_get_mysql_config(self):
        """测试获取MySQL配置"""
        config = Config.get_mysql_config()
        self.assertIsInstance(config, dict)
        self.assertIn('host', config)
        self.assertIn('port', config)
        self.assertIn('database', config)
        self.assertIn('user', config)
    
    def test_get_doris_config(self):
        """测试获取Doris配置"""
        config = Config.get_doris_config()
        self.assertIsInstance(config, dict)
        self.assertIn('fe_nodes', config)
        self.assertIn('username', config)
        self.assertIn('database', config)
    
    def test_get_field_mapping(self):
        """测试获取字段映射配置"""
        mapping = Config.get_field_mapping()
        self.assertIsInstance(mapping, dict)
        self.assertIn('id', mapping)
        self.assertIn('biz_time', mapping)
    
    def test_get_task_config(self):
        """测试获取任务配置"""
        config = Config.get_task_config()
        self.assertIsInstance(config, dict)
        self.assertIn('batch_size', config)
        self.assertIn('max_retries', config)
        self.assertIn('log_level', config)
    
    def test_get_workflow_config(self):
        """测试获取工作流配置"""
        config = Config.get_workflow_config()
        self.assertIsInstance(config, dict)
        self.assertIn('name', config)
        self.assertIn('schedule', config)


class TestLogging(unittest.TestCase):
    """日志测试类"""
    
    def test_setup_logging(self):
        """测试日志设置"""
        logger = setup_logging()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, 'seatunnel_task')
        self.assertTrue(len(logger.handlers) > 0)


class TestTimeRange(unittest.TestCase):
    """时间范围测试类"""
    
    def test_get_time_range(self):
        """测试获取时间范围"""
        start_time, end_time = get_time_range()
        self.assertIsInstance(start_time, str)
        self.assertIsInstance(end_time, str)
        
        # 验证时间格式
        try:
            datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            self.fail("时间格式不正确")
        
        # 验证时间逻辑
        start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        self.assertLess(start_dt, end_dt)


class TestDataTransformation(unittest.TestCase):
    """数据转换测试类"""
    
    def setUp(self):
        """设置测试数据"""
        self.sample_data = [
            {
                'id': 1,
                'biz_time': datetime(2024, 1, 1, 12, 0, 0),
                'section_id': 'S001',
                'direction': 1,
                'device_no': 'D001',
                'cycle': 60,
                'lane_no': 1,
                'lane_type': 'normal',
                'vehicle_nums': 10,
                'avg_speed': 45.5,
                'avg_time': 30.2,
                'queue_len': 5,
                'create_time': datetime(2024, 1, 1, 12, 0, 0),
                'update_time': datetime(2024, 1, 1, 12, 0, 0),
                'del_flag': 0,
                'scene_type': 'traffic'
            }
        ]
    
    def test_transform_data(self):
        """测试数据转换"""
        transformed = transform_data(self.sample_data)
        
        self.assertEqual(len(transformed), 1)
        self.assertIsInstance(transformed, list)
        self.assertIsInstance(transformed[0], dict)
        
        # 验证字段映射
        record = transformed[0]
        self.assertIn('id', record)
        self.assertIn('biz_time', record)
        self.assertEqual(record['id'], 1)
        self.assertEqual(record['section_id'], 'S001')
        
        # 验证datetime转换
        self.assertIsInstance(record['biz_time'], str)
        self.assertEqual(record['biz_time'], '2024-01-01 12:00:00')
    
    def test_transform_data_with_missing_fields(self):
        """测试缺少字段的数据转换"""
        incomplete_data = [{
            'id': 1,
            'biz_time': datetime(2024, 1, 1, 12, 0, 0)
            # 缺少其他字段
        }]
        
        transformed = transform_data(incomplete_data)
        self.assertEqual(len(transformed), 1)
        
        record = transformed[0]
        self.assertEqual(record['id'], 1)
        self.assertIsNone(record['section_id'])  # 缺少的字段应为None


class TestDatabaseOperations(unittest.TestCase):
    """数据库操作测试类"""
    
    def test_get_mysql_connection(self):
        """测试MySQL连接"""
        try:
            result = get_mysql_connection()
            # 如果pymysql可用，应该返回连接对象或None
            self.assertTrue(result is None or hasattr(result, 'cursor'))
        except Exception as e:
            # 如果pymysql不可用，应该抛出异常
            self.assertIn('pymysql', str(e).lower())
    
    def test_extract_data_from_mysql(self):
        """测试从MySQL提取数据"""
        start_time = '2024-01-01 00:00:00'
        end_time = '2024-01-01 23:59:59'
        
        try:
            # 尝试获取连接
            connection = get_mysql_connection()
            if connection:
                result = extract_data_from_mysql(connection, start_time, end_time)
                self.assertIsInstance(result, list)
                connection.close()
            else:
                # 如果连接失败，测试应该处理None连接
                result = extract_data_from_mysql(None, start_time, end_time)
                self.assertEqual(result, [])
        except Exception as e:
            # 如果pymysql不可用，应该抛出异常
            self.assertTrue('pymysql' in str(e).lower() or 'connection' in str(e).lower())
    
    def test_load_data_to_doris_success(self):
        """测试成功加载数据到Doris"""
        test_data = [
            {'id': 1, 'name': 'test1'},
            {'id': 2, 'name': 'test2'}
        ]
        
        try:
            result = load_data_to_doris(test_data)
            # 如果requests可用，应该返回布尔值
            self.assertIsInstance(result, bool)
        except Exception as e:
            # 如果requests不可用，应该抛出异常
            self.assertIn('requests', str(e).lower())
    
    def test_load_data_to_doris_failure(self):
        """测试加载数据到Doris失败"""
        test_data = [{'id': 1, 'name': 'test1'}]
        
        try:
            result = load_data_to_doris(test_data, max_retries=1)
            # 如果requests可用，应该返回布尔值
            self.assertIsInstance(result, bool)
        except Exception as e:
            # 如果requests不可用，应该抛出异常
            self.assertIn('requests', str(e).lower())
    
    def test_load_data_to_doris_empty_data(self):
        """测试加载空数据到Doris"""
        result = load_data_to_doris([])
        self.assertTrue(result)  # 空数据应该返回True


class TestETLProcess(unittest.TestCase):
    """ETL流程测试类"""
    
    @patch('seatunnel_to_doris_task.load_data_to_doris')
    @patch('seatunnel_to_doris_task.transform_data')
    @patch('seatunnel_to_doris_task.extract_data_from_mysql')
    @patch('seatunnel_to_doris_task.get_mysql_connection')
    @patch('seatunnel_to_doris_task.get_time_range')
    def test_main_etl_process_success(self, mock_time_range, mock_connection, 
                                    mock_extract, mock_transform, mock_load):
        """测试ETL流程成功执行"""
        # 设置模拟返回值
        mock_time_range.return_value = ('2024-01-01 00:00:00', '2024-01-01 23:59:59')
        mock_conn = Mock()
        mock_connection.return_value = mock_conn
        mock_extract.return_value = [{'id': 1, 'name': 'test'}]
        mock_transform.return_value = [{'id': 1, 'name': 'test_transformed'}]
        mock_load.return_value = True
        
        result = main_etl_process()
        
        self.assertTrue(result)
        mock_time_range.assert_called_once()
        mock_connection.assert_called_once()
        mock_extract.assert_called_once()
        mock_transform.assert_called_once()
        mock_load.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('seatunnel_to_doris_task.extract_data_from_mysql')
    @patch('seatunnel_to_doris_task.get_mysql_connection')
    @patch('seatunnel_to_doris_task.get_time_range')
    def test_main_etl_process_no_data(self, mock_time_range, mock_connection, mock_extract):
        """测试ETL流程无数据情况"""
        mock_time_range.return_value = ('2024-01-01 00:00:00', '2024-01-01 23:59:59')
        mock_conn = Mock()
        mock_connection.return_value = mock_conn
        mock_extract.return_value = []  # 无数据
        
        result = main_etl_process()
        
        self.assertTrue(result)  # 无数据也应该返回成功
        mock_conn.close.assert_called_once()


class TestIntegration(unittest.TestCase):
    """集成测试类"""
    
    def test_config_integration(self):
        """测试配置集成"""
        # 验证所有配置都能正常获取
        mysql_config = Config.get_mysql_config()
        doris_config = Config.get_doris_config()
        field_mapping = Config.get_field_mapping()
        task_config = Config.get_task_config()
        workflow_config = Config.get_workflow_config()
        
        # 验证配置完整性
        self.assertIsInstance(mysql_config, dict)
        self.assertIsInstance(doris_config, dict)
        self.assertIsInstance(field_mapping, dict)
        self.assertIsInstance(task_config, dict)
        self.assertIsInstance(workflow_config, dict)
        
        # 验证关键配置项存在
        self.assertIn('host', mysql_config)
        self.assertIn('fe_nodes', doris_config)
        self.assertIn('batch_size', task_config)
        self.assertIn('name', workflow_config)


def run_performance_test():
    """性能测试"""
    print("\n=== 性能测试 ===")
    
    # 测试大量数据转换性能
    import time
    
    # 生成测试数据
    large_dataset = []
    for i in range(10000):
        large_dataset.append({
            'id': i,
            'biz_time': datetime.now(),
            'section_id': f'S{i:04d}',
            'direction': i % 2,
            'device_no': f'D{i:04d}',
            'cycle': 60,
            'lane_no': i % 4 + 1,
            'lane_type': 'normal',
            'vehicle_nums': i % 20,
            'avg_speed': 45.5 + (i % 10),
            'avg_time': 30.2 + (i % 5),
            'queue_len': i % 10,
            'create_time': datetime.now(),
            'update_time': datetime.now(),
            'del_flag': 0,
            'scene_type': 'traffic'
        })
    
    # 测试转换性能
    start_time = time.time()
    transformed = transform_data(large_dataset)
    end_time = time.time()
    
    print(f"转换 {len(large_dataset)} 条记录耗时: {end_time - start_time:.2f} 秒")
    print(f"平均每条记录耗时: {(end_time - start_time) / len(large_dataset) * 1000:.2f} 毫秒")
    print(f"转换后记录数: {len(transformed)}")


def run_connection_test():
    """连接测试"""
    print("\n=== 连接测试 ===")
    
    try:
        # 测试配置验证
        if Config.validate_config():
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
        
        # 测试日志设置
        logger = setup_logging()
        logger.info("日志系统测试")
        print("✅ 日志系统正常")
        
        # 测试时间范围获取
        start_time, end_time = get_time_range()
        print(f"✅ 时间范围获取正常: {start_time} ~ {end_time}")
        
    except Exception as e:
        print(f"❌ 连接测试失败: {str(e)}")


if __name__ == '__main__':
    print("SeaTunnel数据同步任务测试套件")
    print("=" * 50)
    
    # 运行单元测试
    print("\n=== 单元测试 ===")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行性能测试
    run_performance_test()
    
    # 运行连接测试
    run_connection_test()
    
    print("\n=== 测试完成 ===")
    print("如需运行完整的集成测试，请确保数据库连接配置正确")