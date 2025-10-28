# PostgreSQL 配置文件
DB_CONFIG = {
    'db_type': 'postgresql',      # 可选: mysql, postgresql, sqlite
    'username': 'postgres',
    'password': '123456',
    'host': 'localhost',
    'port': '5432',
    'database': 'lianghua',
}

# 数据库主机地址
DB_HOST = DB_CONFIG['host']
# 数据库端口号，默认是 5432
DB_PORT = int(DB_CONFIG['port'])
# 数据库用户名
DB_USER = DB_CONFIG['username']
# 数据库用户密码
DB_PASSWORD = DB_CONFIG['password']
# 数据库名称
DB_NAME = DB_CONFIG['database']
