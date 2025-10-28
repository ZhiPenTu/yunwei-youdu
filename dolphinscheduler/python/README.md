# SeaTunnel to DolphinScheduler 数据同步任务

## 项目概述

本项目将原始的SeaTunnel配置文件转换为符合DolphinScheduler规范的Python脚本，实现从MySQL数据库到Doris数据库的数据同步功能。

## 功能特性

- ✅ **完整保留原文件功能逻辑**：实现MySQL到Doris的数据同步
- ✅ **严格遵循Python PEP8编码规范**：代码格式化和命名规范
- ✅ **适配DolphinScheduler执行环境**：使用PyDolphinScheduler SDK
- ✅ **异常处理和日志记录**：完善的错误处理和日志输出
- ✅ **动态时间参数支持**：支持`$[yyyyMM]`和`$[yyyyMMdd-1]`参数
- ✅ **字段映射转换**：完整的字段映射功能
- ✅ **Stream Load数据加载**：使用Doris Stream Load API

## 文件结构

```
dolphinscheduler/python/
├── seatunnel_to_doris_task.py  # 主要的Python任务脚本
├── requirements.txt            # Python依赖包列表
├── README.md                  # 项目说明文档
└── test.text                  # 原始SeaTunnel配置文件
```

## 原始配置分析

### SeaTunnel配置结构

原始`test.text`文件包含以下组件：

1. **环境配置 (env)**
   - 并行度：1
   - 作业模式：BATCH
   - 检查点间隔：1000ms

2. **数据源 (source)**
   - 类型：MySQL JDBC
   - 连接信息：35.46.5.36:3306/vrc
   - 查询：`t_statistics_info_min_$[yyyyMM]`表的增量数据

3. **数据转换 (transform)**
   - 字段映射：16个字段的1:1映射

4. **数据输出 (sink)**
   - 类型：Apache Doris
   - 目标：35.46.5.98:8030/db_htcf
   - 格式：JSON格式，按行读取

## 安装和配置

### 1. 环境要求

- Python 3.9+
- DolphinScheduler 3.1.0+
- 网络访问MySQL和Doris服务器

### 2. 安装依赖

```bash
cd /Users/tuzhipeng/Desktop/航天长峰/运维有肚/dolphinscheduler/python
pip install -r requirements.txt
```

### 3. 配置DolphinScheduler

确保DolphinScheduler API服务器已启动并启用Python Gateway：

```bash
# 启用Python Gateway服务
export API_PYTHON_GATEWAY_ENABLED="true"

# 启动DolphinScheduler API服务器
./bin/dolphinscheduler-daemon.sh start api-server
```

### 4. 配置连接信息

根据实际环境修改脚本中的数据库连接配置：

```python
# MySQL源数据库配置
self.mysql_config = {
    'host': '35.46.5.36',        # MySQL服务器地址
    'port': 3306,                # MySQL端口
    'database': 'vrc',           # 数据库名
    'user': 'root',              # 用户名
    'password': 'HTcf2022!@#',   # 密码（生产环境请使用环境变量）
    # ...
}

# Doris目标数据库配置
self.doris_config = {
    'fe_nodes': '35.46.5.98:8030',  # Doris FE节点地址
    'username': 'root',             # Doris用户名
    'password': '',                 # Doris密码
    'database': 'db_htcf',          # 目标数据库
    # ...
}
```

## 使用方法

### 1. 直接运行脚本

```bash
python seatunnel_to_doris_task.py
```

### 2. 在DolphinScheduler中创建工作流

```python
from seatunnel_to_doris_task import create_dolphinscheduler_workflow

# 创建并提交工作流
create_dolphinscheduler_workflow()
```

### 3. 通过DolphinScheduler Web UI

1. 登录DolphinScheduler Web界面
2. 创建新的工作流项目
3. 添加Python任务节点
4. 将脚本内容复制到任务定义中
5. 配置调度参数
6. 提交并启动工作流

## 核心功能说明

### 1. 时间参数处理

脚本自动处理SeaTunnel中的时间参数：

- `$[yyyyMM]`：当前年月，如`202401`
- `$[yyyyMMdd-1]`：昨天日期，如`20240115`

### 2. 数据提取 (Extract)

```python
def extract_data_from_mysql(self, query: str) -> List[Dict[str, Any]]:
    """从MySQL提取数据，支持动态表名和时间过滤"""
```

### 3. 数据转换 (Transform)

```python
def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """应用字段映射规则进行数据转换"""
```

### 4. 数据加载 (Load)

```python
def load_data_to_doris(self, data: List[Dict[str, Any]], time_params: Dict[str, str]) -> bool:
    """使用Stream Load API将数据加载到Doris"""
```

## 调度配置

默认调度配置：

```python
with Workflow(
    name="seatunnel_mysql_to_doris_sync",
    schedule="0 0 1 * * ? *",  # 每天凌晨1点执行
    start_time="2024-01-01",
    tenant="default"
) as workflow:
```

调度表达式说明：
- `0 0 1 * * ? *`：每天凌晨1点执行
- 格式：`秒 分 时 日 月 周 年`

## 日志和监控

### 日志配置

脚本配置了双重日志输出：
- 控制台输出：实时查看执行状态
- 文件输出：`/tmp/seatunnel_task.log`

### 监控指标

脚本记录以下关键指标：
- 数据提取记录数
- 数据转换成功率
- Doris加载状态
- 执行时间和异常信息

## 错误处理

### 常见错误及解决方案

1. **MySQL连接失败**
   ```
   错误：pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")
   解决：检查网络连接和MySQL服务状态
   ```

2. **Doris Stream Load失败**
   ```
   错误：Stream Load请求失败: 400
   解决：检查Doris集群状态和表结构
   ```

3. **时间参数解析错误**
   ```
   错误：生成时间参数失败
   解决：检查系统时间设置
   ```

## 性能优化建议

1. **批量处理**：根据数据量调整批次大小
2. **连接池**：在高频执行场景下使用连接池
3. **并行处理**：对于大数据量可考虑分片并行处理
4. **监控告警**：配置DolphinScheduler告警规则

## 安全注意事项

1. **密码管理**：生产环境使用环境变量或密钥管理系统
2. **网络安全**：确保数据库连接使用SSL加密
3. **权限控制**：使用最小权限原则配置数据库用户
4. **日志安全**：避免在日志中输出敏感信息

## 版本兼容性

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.9+ | 支持类型提示和现代语法 |
| DolphinScheduler | 3.1.0+ | 支持PyDolphinScheduler SDK |
| PyMySQL | 1.0.2+ | MySQL连接驱动 |
| Requests | 2.28.0+ | HTTP请求库 |

## 贡献指南

1. Fork项目仓库
2. 创建功能分支
3. 提交代码变更
4. 创建Pull Request
5. 等待代码审查

## 许可证

本项目遵循Apache 2.0许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues：提交技术问题
- 邮件联系：技术支持邮箱
- 文档更新：欢迎提交文档改进建议