import akshare as ak
import datetime
from scheduler_case.config import scheduler
from db.database import PostgresDB




@scheduler.task(id='get_stock_market_activity_legu_df22', trigger='interval', seconds=1)
def stock_market_activity_legu_df():
    stock_market_activity_legu_df = ak.stock_market_activity_legu()
    # 保存到数据库
    db = PostgresDB()
    with db.get_session() as session:
        stock_market_activity_legu_df.to_sql('stock_market_activity_legu', session.bind, if_exists='replace', index=False)


# 测试
if __name__ == '__main__':
    stock_market_activity_legu_df()