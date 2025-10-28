from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base
from model.TimestampMixin import TimestampMixin

Base = declarative_base()



class BaseModelInteger(Base, TimestampMixin):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
