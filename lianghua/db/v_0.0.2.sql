-- 创建存储市场数据的表,将 item 拆分为多个字段
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    -- 上涨数量,保留两位小数
    rising NUMERIC(10, 2),
    -- 涨停数量,保留两位小数
    limit_up NUMERIC(10, 2),
    -- 实际涨停数量,保留两位小数
    real_limit_up NUMERIC(10, 2),
    -- ST 股涨停数量,保留两位小数
    st_limit_up NUMERIC(10, 2),
    -- 下跌数量,保留两位小数
    falling NUMERIC(10, 2),
    -- 跌停数量,保留两位小数
    limit_down NUMERIC(10, 2),
    -- 实际跌停数量,保留两位小数
    real_limit_down NUMERIC(10, 2),
    -- ST 股跌停数量,保留两位小数
    st_limit_down NUMERIC(10, 2),
    -- 平盘数量,保留两位小数
    flat NUMERIC(10, 2),
    -- 停牌数量,保留两位小数
    suspension NUMERIC(10, 2),
    -- 活跃数量,保留两位小数
    activity NUMERIC(10, 2),
    -- 统计日期
    stat_date TIMESTAMP 
);
COMMENT ON COLUMN market_data.id IS '表的主键,自增序列';
COMMENT ON COLUMN market_data.rising IS '上涨数量,保留两位小数';
COMMENT ON COLUMN market_data.limit_up IS '涨停数量,保留两位小数';
COMMENT ON COLUMN market_data.real_limit_up IS '实际涨停数量,保留两位小数';
COMMENT ON COLUMN market_data.st_limit_up IS 'ST 股涨停数量,保留两位小数';
COMMENT ON COLUMN market_data.falling IS '下跌数量,保留两位小数';
COMMENT ON COLUMN market_data.limit_down IS '跌停数量,保留两位小数';
COMMENT ON COLUMN market_data.real_limit_down IS '实际跌停数量,保留两位小数';
COMMENT ON COLUMN market_data.st_limit_down IS 'ST 股跌停数量,保留两位小数';
COMMENT ON COLUMN market_data.flat IS '平盘数量,保留两位小数';
COMMENT ON COLUMN market_data.suspension IS '停牌数量,保留两位小数';
COMMENT ON COLUMN market_data.activity IS '活跃数量,保留两位小数';
COMMENT ON COLUMN market_data.stat_date IS '统计日期';
