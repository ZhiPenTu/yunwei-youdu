-- 创建一个名为 version_info 的表,用于存储版本相关信息
CREATE TABLE IF NOT EXISTS version_history (
    -- 自增的 ID 字段,作为主键
    id SERIAL PRIMARY KEY,
    -- 版本号字段,使用 VARCHAR 类型存储
    version VARCHAR(20) NOT NULL,
    -- 创建时间字段,使用 TIMESTAMP 类型,默认值为当前时间
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN version_history.version IS '版本号,用于记录数据库的版本';
COMMENT ON COLUMN version_history.update_time IS '更新时间,记录每次数据库版本变更的时间';


