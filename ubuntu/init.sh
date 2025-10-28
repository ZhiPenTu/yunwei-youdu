# 分别为三台机器设置主机名
sudo hostnamectl set-hostname "node01"      
sudo hostnamectl set-hostname "node02"     
sudo hostnamectl set-hostname "node03"  

#2.4 域名写入host文件
cat >> /etc/hosts << EOF
192.168.2.101 node01
192.168.2.102 node02
192.168.2.103 node03
EOF


# 2.5 时间同步
# 分布式要解决的一个问题就是时钟同步，这里我们借助阿里云服务，实现集群节点与阿里云时钟同步 设置时区为上海
timedatectl set-timezone Asia/Shanghai

#安装ntpdate并与阿里云同步
sudo apt install -y ntpsec-ntpdate
ntpdate ntp.aliyun.com
#选择一个合适的编辑器，然后在配置末尾加上如下代码，表示每晚0点执行同步命令
0 0 * * * ntpdate ntp.aliyun.com

#2.6 配置内核转发和网桥过滤
#生成配置
cat << EOF | tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF


cat << EOF | tee ipvs.sh
#!/bin/sh
modprobe -- ip_vs
modprobe -- ip_vs_rr
modprobe -- ip_vs_wrr
modprobe -- ip_vs_sh
modprobe -- nf_conntrack
EOF


echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null


sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin



{  
  "registry-mirrors": [  
    "https://docker.1ms.run",  
    "https://doublezonline.cloud",  
    "https://dislabaiot.xyz",  
    "https://docker.fxxk.dedyn.io",  
    "https://dockerpull.org",  
    "https://docker.unsee.tech",  
    "https://hub.rat.dev",  
    "https://docker.nastool.de",  
    "https://docker.zhai.cm",  
    "https://docker.5z5f.com",  
    "https://a.ussh.net",  
    "https://docker.udayun.com",  
    "https://hub.geekery.cn",
    "https://docker.1panel.live",
    "https://dockerproxy.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://ccr.ccs.tencentyun.com",
    "https://mirrors.tuna.tsinghua.edu.cn",
    "http://mirrors.sohu.com",
    "https://ustc-edu-cn.mirror.aliyuncs.com",
    "https://docker.m.daocloud.io",
    "https://docker.awsl9527.cn"  
  ],
  "insecure-registries": ["kubernetes-register.sswang.com"],
  "exec-opts": [  
    "native.cgroupdriver=systemd"  
  ]  
}

wget https://github.com/Mirantis/cri-dockerd/releases/download/v0.3.16/cri-dockerd-0.3.16.arm64.tgz


cat > /etc/systemd/system/cri-dockerd.service<<-EOF
[Unit]
Description=CRI Interface for Docker Application Container Engine
Documentation=https://docs.mirantis.com
After=network-online.target firewalld.service docker.service
Wants=network-online.target
Requires=cri-docker.socket     #system cri-docker.socket  文件名
 
[Service]
Type=notify
ExecStart=/usr/local/bin/cri-dockerd --pod-infra-container-image=registry.cn-hangzhou.aliyuncs.com/google_containers/pause:3.10
 --network-plugin=cni --cni-conf-dir=/etc/cni/net.d --cni-bin-dir=/opt/cni/bin --container-runtime-endpoint=unix:///var/run/cri-dockerd.sock --cri-dockerd-root-directory=/var/lib/dockershim --docker-endpoint=unix:///var/run/docker.sock --cri-dockerd-root-directory=/var/lib/docker
ExecReload=/bin/kill -s HUP $MAINPID
TimeoutSec=0
RestartSec=2
Restart=always
StartLimitBurst=3
StartLimitInterval=60s
LimitNOFILE=infinity
LimitNPROC=infinity
LimitCORE=infinity
TasksMax=infinity
Delegate=yes
KillMode=process
[Install]
WantedBy=multi-user.target
EOF


cat > /etc/systemd/system/cri-docker.socket <<-EOF
[Unit]
Description=CRI Docker Socket for the API
PartOf=cri-docker.service    #systemd cri-docker.servics 文件名
 
[Socket]
ListenStream=/var/run/cri-dockerd.sock
SocketMode=0660
SocketUser=root
SocketGroup=docker
 
[Install]
WantedBy=sockets.target
EOF


curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list


kubeadm init --kubernetes-version=1.32.2 --control-plane-endpoint=node01 --apiserver-advertise-address=192.168.2.101 --pod-network-cidr=10.244.0.0/16 --service-cidr=10.96.0.0/12 --image-repository=registry.aliyuncs.com/google_containers --cri-socket=unix:///var/run/cri-dockerd.sock --upload-certs --v=9




  kubeadm join node01:6443 --token cnyony.kne3xnpby4ycdovh \
        --discovery-token-ca-cert-hash sha256:525ba32c521397beb7705b8e7662d90e2470a484bb83104713b743ce25f5fb6b \
        --control-plane --certificate-key 457b1cfed01d3e8b1cb6e0631f0529fe2aed103e9e69f46047928e650693e4bb

kubeadm join node01:6443 --token cnyony.kne3xnpby4ycdovh --discovery-token-ca-cert-hash sha256:525ba32c521397beb7705b8e7662d90e2470a484bb83104713b743ce25f5fb6b --cri-socket=unix:///var/run/cri-dockerd.sock  

请分析3月27号A股中大盘和各个板块的数据，优先参考同花顺公开的数据，
  1.要求整理成表格， 表头为 “板块名称”， “涨幅”，“成交额”， “主力净额”， “总流入”，并计算 "主力强度"，"散户强度"，要求分析至少10 个板块，要包含证券，银行板块
  2.主力强度的计算公式为：(主力净额/成交额)*100
  3.散户强度的计算公式为: (总流入-主力净额/成交额)*100
  4.要求在表格中添加2个列，名为 “主力行为”，“散户行为”，如果主力强度为 1～3标记建仓，-1～1为洗盘，大于等于 3为抢筹，小于等于-1 为出货

