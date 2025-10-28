#!/bin/bash

# 后台启动JAR包并记录PID
nohup java -jar ./cvis-test.jar > app.log 2>&1 & echo $! > cvis-test-app.pid

echo "应用已启动，PID: $(cat cvis-test-app.pid)"