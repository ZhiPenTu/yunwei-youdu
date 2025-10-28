DROP TABLE t_statistics_info_min_202504
CREATE TABLE iot_analyse_test1.t_statistics_info_min_all (
  id BIGINT,
  biz_time DATETIME,
  section_id INT,
  direction TINYINT,
  device_no VARCHAR(64),
  cycle INT,
  lane_type TINYINT,
  vehicle_nums INT,
  avg_speed DECIMAL(10, 2),
  avg_space DECIMAL(10, 2),
  avg_time DECIMAL(10, 2),
  queue_len DECIMAL(10, 2),
  create_time DATETIME,
  update_time DATETIME,
  del_flag TINYINT,
  scene_type VARCHAR(20)
) ENGINE = OLAP UNIQUE KEY(id, biz_time) PARTITION BY RANGE(biz_time) () DISTRIBUTED BY HASH(biz_time) PROPERTIES (
  "replication_num" = "1",
  "dynamic_partition.enable" = "true",
  "dynamic_partition.time_unit" = "MONTH",
  "dynamic_partition.end" = "2",
  "dynamic_partition.prefix" = "p",
  "dynamic_partition.buckets" = "8",
  "dynamic_partition.start_day_of_month" = "3"
)

DROP TABLE t_statistics_info_min_device_202504
CREATE TABLE iot_analyse_test1.t_statistics_info_min_device_202504 (
    id                 VARCHAR(64),
    deviceNo           VARCHAR(64),
    direction          TINYINT,
    vehicleNums        INT,
    bizTime            DATETIME
) ENGINE=OLAP
UNIQUE KEY(id)
DISTRIBUTED BY HASH(id) BUCKETS 10
PROPERTIES (
    "replication_num" = "1",
    "enable_unique_key_merge_on_write" = "true"
);



  Doris {
        plugin_output = "fake1"
        fenodes = "35.46.5.52:8030"
        username = root
        password = ""
        database = "iot_analyse_test1"
        table = "t_statistics_info_min_device_202504"
        sink.enable-2pc = "false"
        sink.label-prefix = "iot_json"
        doris.config = {
            format="json"
            read_json_by_line="true"
        }
    }