-- 创建用于存储股票信息的表格
CREATE TABLE IF NOT EXISTS stocks (
    -- 股票代码,作为主键
    id VARCHAR(50) PRIMARY KEY,
    -- 简称,不可为空
    name VARCHAR(50) NOT NULL,
    -- 上市时间,不可为空
    list_date VARCHAR(50) NOT NULL,
    -- 所属行业,不可为空
    industry VARCHAR(50) NOT NULL,
    -- 交易所,如 SH 表示上交所，SZ 表示深交所
    exchange VARCHAR(10) NOT NULL,
    -- 更新时间
    updated_at VARCHAR(50),
    -- 创建时间
    created_at VARCHAR(50)
);

COMMENT ON TABLE stocks IS '股票模型';
COMMENT ON COLUMN stocks.id IS '股票代码';
COMMENT ON COLUMN stocks.name IS '简称';
COMMENT ON COLUMN stocks.list_date IS '上市时间';
COMMENT ON COLUMN stocks.industry IS '所属行业';
COMMENT ON COLUMN stocks.exchange IS '交易所,如 SH 表示上交所，SZ 表示深交所';
-- 更新时间
COMMENT ON COLUMN stocks.updated_at IS '更新时间';
-- 创建时间
COMMENT ON COLUMN stocks.created_at IS '创建时间';

-- -- 创建一个名为 stocks_data 的表,用于存储股票日线数据
-- CREATE TABLE IF NOT EXISTS stocks_data (
--     -- 股票代码,作为主键,关联 stocks 表的 id 字段
--     stock_id VARCHAR(50) REFERENCES stocks(id) PRIMARY KEY,
--     -- 日期,不可为空
--     date VARCHAR(50) NOT NULL,
--     -- 开盘价,不可为空
--     open VARCHAR(50) NOT NULL,
--     -- 收盘价,不可为空
--     close VARCHAR(50) NOT NULL,
--     -- 最高价,不可为空
--     high VARCHAR(50) NOT NULL,
--     -- 最低价,不可为空
--     low VARCHAR(50) NOT NULL,
--     -- 成交量,不可为空
--     volume VARCHAR(50) NOT NULL,
--     -- 成交额,不可为空
--     amount VARCHAR(50) NOT NULL,
--     -- 振幅,不可为空
--     pct_chg VARCHAR(50) NOT NULL,
--     -- 涨跌幅,不可为空
--     change VARCHAR(50) NOT NULL,
--     -- 换手率,不可为空
--     turnover_rate VARCHAR(50) NOT NULL,
--     -- 更新时间
--     updated_at VARCHAR(50),
--     -- 创建时间
--     created_at VARCHAR(50)
-- );

-- COMMENT ON TABLE stocks_data IS '股票日线数据';
-- COMMENT ON COLUMN stocks_data.stock_id IS '股票代码';
-- COMMENT ON COLUMN stocks_data.date IS '日期';
-- COMMENT ON COLUMN stocks_data.open IS '开盘价';
-- COMMENT ON COLUMN stocks_data.close IS '收盘价';
-- COMMENT ON COLUMN stocks_data.high IS '最高价';
-- COMMENT ON COLUMN stocks_data.low IS '最低价';
-- COMMENT ON COLUMN stocks_data.volume IS '成交量';
-- COMMENT ON COLUMN stocks_data.amount IS '成交额';
-- COMMENT ON COLUMN stocks_data.pct_chg IS '振幅';
-- COMMENT ON COLUMN stocks_data.change IS '涨跌幅';
-- COMMENT ON COLUMN stocks_data.turnover_rate IS '换手率';
-- -- 更新时间
-- COMMENT ON COLUMN stocks_data.updated_at IS '更新时间';
-- -- 创建时间
-- COMMENT ON COLUMN stocks_data.created_at IS '创建时间';
