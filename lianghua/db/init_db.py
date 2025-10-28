from flask import Flask
import psycopg2
import os
import re
from db.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
def init_db(app: Flask):
    """
    初始化数据库的函数，可作为 Flask 的函数入口使用
    """
    with app.app_context():
        # 从 Flask 配置中获取数据库连接信息
        db_config = {
            'host': DB_HOST,
            'port': DB_PORT,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'database': DB_NAME
        }
        try:
            # 连接到 PostgreSQL 数据库
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            # 获取当前文件所在目录,
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # 检查 version_history 表是否已存在，如果不存在则执行 init.sql
            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'version_history')")
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                # 执行 init.sql 文件来初始化数据库版本管理表
                init_sql_path = os.path.join(current_dir, 'init.sql')
                if os.path.exists(init_sql_path):
                    with open(init_sql_path, 'r') as f:
                        init_sql = f.read()
                        cursor.execute(init_sql)
                        conn.commit()

            # 获取当前数据库版本
            cursor.execute("SELECT version FROM version_history")
            result = cursor.fetchall()
            print(result)
            # 判断是否存在版本号
            if result:
                # 获取版本号最大的
                current_version = max(result, key=lambda x: x[0])[0]
            else:
                current_version = '0.0.0'
                # 初始化版本号
                cursor.execute("INSERT INTO version_history (version) VALUES (%s)", (current_version,))
                conn.commit()

            print(f"当前版本号{current_version}")

            # 获取所有 v_x.x.x.sql 文件并排序
            version_pattern = re.compile(r'v_(\d+\.\d+\.\d+)\.sql')
            sql_files = []
            for f in os.listdir(current_dir):
                match = version_pattern.match(f)
                if match:
                    version_str = match.group(1)
                    sql_files.append((version_str, f))
            sql_files.sort(key=lambda x: [int(part) for part in x[0].split('.')])
            print(sql_files)

            # 根据版本号更新数据库
            for version_str, sql_file in sql_files:
                try:
                    version_parts = [int(part) for part in version_str.split('.')]
                    current_version_parts = [int(part) for part in current_version.split('.')]
                    if version_parts > current_version_parts:
                        sql_file_path = os.path.join(current_dir, sql_file)
                        with open(sql_file_path, 'r') as f:
                            sql_statements = f.read()
                            cursor.execute(sql_statements)
                        # 更新数据库版本号
                        # cursor.execute("DELETE FROM version_history")
                        cursor.execute("INSERT INTO version_history (version) VALUES (%s)", (version_str,))
                        current_version = version_str
                except ValueError:
                    print(f"无法解析文件 {sql_file} 的版本号")

            conn.commit()
        except psycopg2.Error as e:
            print(f"数据库操作出错: {e}")
            if conn:
                conn.rollback()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

