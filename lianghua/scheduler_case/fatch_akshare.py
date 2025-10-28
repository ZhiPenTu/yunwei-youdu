# import datetime
# import akshare as ak
# from scheduler_case.config import scheduler
# from db.database import PostgresDB
# from pytz import timezone



# @scheduler.task(id='do_job_1', trigger='interval', seconds=2)
# def tiem_2seconds():
#     current_time = datetime.datetime.now()
#     print("22222装饰器定时任务开始执行时间：{}".format(current_time))


# @scheduler.task(id='do_job_2', trigger='interval', seconds=5)
# def time_5seconds():
#     current_time = datetime.datetime.now()
#     print("5555555装饰器定时任务开始执行时间：{}".format(current_time))






# @scheduler.task(
#     id='get_stock_market_activity_legu_df',
#     trigger='cron',
#     day_of_week='mon-fri',
#     hour='9-15',
#     minute='*/1',
#     timezone=timezone('Asia/Shanghai'),
#     start_date='2024-06-15 09:15:00',
#     end_date='2024-06-15 15:00:00'
# )
# def stock_market_activity_legu_df():
#     try:
#         # 获取数据
#         df = ak.stock_market_activity_legu()
        
#         # 初始化数据库连接
#         db = PostgresDB()
#         engine = db.get_engine()
        
#         # 保存到数据库
#         with engine.begin() as connection:
#             df.to_sql('stock_market_activity_legu', 
#                       con=connection,
#                       if_exists='append',
#                       index=False,
#                       method='multi')
#             print(f"[{datetime.now(timezone('Asia/Shanghai'))}] 数据获取成功")
#             engine.dispose()
#     except Exception as e:
#         print(f"[{datetime.now()}] 数据获取或保存失败：{str(e)}")
