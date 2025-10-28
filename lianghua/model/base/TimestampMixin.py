from sqlalchemy import Column, DateTime, func

# 创建带有时间戳的基础模型
class TimestampMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)