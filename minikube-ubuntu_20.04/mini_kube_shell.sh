#!/bin/bash
minikube start  --force --image-mirror-country='cn' --driver=docker --nodes=3 --memory=no-limit --cpus=no-limit --network-plugin=cni --cni=calico

helm upgrade --install -n kubesphere-system --create-namespace ks-core https://charts.kubesphere.com.cn/main/ks-core-1.1.4.tgz --debug --wait --set global.imageRegistry=swr.cn-southwest-2.myhuaweicloud.com/ks


export https_proxy=http://127.0.0.1:6152;export http_proxy=http://127.0.0.1:6152;export all_proxy=socks5://127.0.0.1:6153