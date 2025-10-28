#!/bin/bash

# SeaTunnel连接器下载脚本
# 用法：./download_connectors.sh <版本号> [目标目录]

VERSION=2.3.10
TARGET_DIR=${2:-"./connectors"}

# 需要下载的连接器列表（示例列表，可根据实际需求修改）
CONNECTORS=(
    "connector-amazondynamodb"
    "connector-assert"
    "connector-cassandra"
    "connector-cdc-mysql"
    "connector-cdc-mongodb"
    "connector-cdc-sqlserver"
    "connector-cdc-postgres"
    "connector-cdc-oracle"
    "connector-cdc-tidb"
    "connector-clickhouse"
    "connector-datahub"
    "connector-dingtalk"
    "connector-doris"
    "connector-elasticsearch"
    "connector-email"
    "connector-file-ftp"
    "connector-file-hadoop"
    "connector-file-local"
    "connector-file-oss"
    "connector-file-jindo-oss"
    "connector-file-s3"
    "connector-file-sftp"
    "connector-file-obs"
    "connector-google-sheets"
    "connector-google-firestore"
    "connector-hive"
    "connector-http-base"
    "connector-http-feishu"
    "connector-http-gitlab"
    "connector-http-github"
    "connector-http-jira"
    "connector-http-klaviyo"
    "connector-http-lemlist"
    "connector-http-myhours"
    "connector-http-notion"
    "connector-http-onesignal"
    "connector-http-wechat"
    "connector-hudi"
    "connector-iceberg"
    "connector-influxdb"
    "connector-iotdb"
    "connector-jdbc"
    "connector-kafka"
    "connector-kudu"
    "connector-maxcompute"
    "connector-mongodb"
    "connector-neo4j"
    "connector-openmldb"
    "connector-pulsar"
    "connector-rabbitmq"
    "connector-redis"
    "connector-druid"
    "connector-s3-redshift"
    "connector-sentry"
    "connector-slack"
    "connector-socket"
    "connector-starrocks"
    "connector-tablestore"
    "connector-selectdb-cloud"
    "connector-hbase"
    "connector-amazonsqs"
    "connector-easysearch"
    "connector-paimon"
    "connector-rocketmq"
    "connector-tdengine"
    "connector-web3j"
    "connector-milvus"
    "connector-activemq"
    "connector-prometheus"
    "connector-sls"
    "connector-qdrant"
    "connector-typesense"
    "connector-cdc-opengauss"
    "seatunnel-transforms-v2"  # 必须的公共依赖
)

# 创建目标目录
mkdir -p "$TARGET_DIR"

# 下载函数
download_connector() {
    local artifact=$1
    local url="https://repo.maven.apache.org/maven2/org/apache/seatunnel/${artifact}/${VERSION}/${artifact}-${VERSION}.jar"
    
    echo "正在下载: $artifact-$VERSION.jar"
    if wget -q --show-progress -P "$TARGET_DIR" "$url"; then
        echo "✅ 下载成功: $artifact"
    else
        echo "❌ 下载失败: $artifact"
        exit 1
    fi
}

# 主下载循环
for connector in "${CONNECTORS[@]}"; do
    download_connector "$connector"
done

echo "========================================"
echo "所有连接器已下载到目录: $TARGET_DIR"


cp /opt/seatunnel/apache-seatunnel-2.3.10/config/hazelcast-client.yaml /opt/seatunnel/apache-seatunnel-web-1.0.2-bin/conf/
cp /opt/seatunnel/apache-seatunnel-2.3.10/connectors/plugin-mapping.properties /opt/seatunnel/apache-seatunnel-web-1.0.2-bin/conf/

cp /opt/seatunnel/apache-seatunnel-2.3.10/lib/connector-*.jar /opt/seatunnel/apache-seatunnel-web-1.0.0-bin/libs

export SEATUNNEL_HOME=  
export PATH=$PATH:$SEATUNNEL_HOME/bin
sudo sh /opt/seatunnel/apache-seatunnel-web-1.0.2-bin/bin/seatunnel-backend-daemon.sh start