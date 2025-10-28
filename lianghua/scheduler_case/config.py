import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler
# 定义定时任务配置 使用单例避免多次加载
class MyScheduler(object):
    _instance = None # 初始值
    APScheduler = None # 初始值

    def __new__(cls, *args, **kw):
        if cls._instance is None:
        	# 第一次初始的时候None ,就做初始化的操作，如果不是第一次就返回第一次生成的对象
            # cls.APScheduler = APScheduler(scheduler=BackgroundScheduler(daemon=True))
            cls.APScheduler = APScheduler()
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        pass

scheduler = MyScheduler().APScheduler 