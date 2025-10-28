from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from contextlib import contextmanager
from typing import Generator, Any
import threading
from db.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT,DB_NAME
# 数据库连接字符串
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# 创建数据库引擎，考虑性能，使用连接池
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # 优化后的连接池大小
    max_overflow=20,  # 增加溢出连接数
    pool_timeout=15,  # 缩短获取连接超时时间
    pool_recycle=1800,  # 更积极的连接回收策略
    pool_pre_ping=True,  # 增加连接健康检查
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
    , echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 创建基类
Base = declarative_base()
class PostgresDB:
    _local = threading.local()

    @contextmanager
    def get_session(self) -> Generator[Any, None, None]:
        if not hasattr(self._local, "session"):
            self._local.session = SessionLocal()
        try:
            yield self._local.session
            self._local.session.commit()
        except Exception as e:
            self._local.session.rollback()
            raise e
        finally:
            self._local.session.close()
            del self._local.session


# 以下是调用示例:
if __name__ == "__main__":
    # 创建 PostgresDB 实例
    db = PostgresDB()

    try:
        # 使用上下文管理器示例
        with db.get_session() as session:
            # 执行简单查询验证连接
            result = session.execute(text("SELECT version()"))
            print("PostgreSQL 版本:", result.scalar())

            # 查询当前连接数
            connections = session.execute(
                text("SELECT count(*) FROM pg_stat_activity WHERE pid <> pg_backend_pid()")
            ).scalar()
            print(f"当前活跃连接数: {connections}")

    except Exception as e:
        print(f"数据库操作出错: {e}")
