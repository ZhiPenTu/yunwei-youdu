import os

from flask import Flask
# import flaskr.auth as auth
# import flaskr.blog as blog
import config
from scheduler_case.config import scheduler
from scheduler_case import fatch_akshare
from db.init_db import init_db

from service.StocksService import StocksService

 
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # 初始化数据库
    init_db(app)
    # 注册博客蓝图
    # app.register_blueprint(auth.bp)
    # app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    
    stock_service = StocksService()
    stock_service.get_data()
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    app.config['SCHEDULER_API_ENABLED'] = True  # 启用 API
    
    #配置执行器
    app.config['SCHEDULER_EXECUTORS'] = {'default': {'type': 'threadpool', 'max_workers': 10}}
    #配置作业存储器
    app.config['SCHEDULER_JOBSTORES'] = {'default': {'type': 'memory'}}
    app.config.from_object(config.Config)
    if not scheduler.running:
        scheduler.init_app(app)
        scheduler.start()
        print(scheduler.get_jobs())
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False)
