from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base
from model.TimestampMixin import TimestampMixin

Base = declarative_base()



class BaseModelString(Base, TimestampMixin):
    __abstract__ = True
    id = Column(String, primary_key=True, index=True)
