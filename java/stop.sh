#!/bin/bash

PID_FILE="cvis-test-app.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "未找到PID文件"
    exit 1
fi

PID=$(cat $PID_FILE)
if ps -p $PID > /dev/null; then
    kill -9 $PID
    echo "已终止进程: $PID"
    rm $PID_FILE
else
    echo "进程 $PID 未运行"
    rm $PID_FILE
fi