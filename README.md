# etcd_test

```
etcd_test/
├── confd                        # confd配置文件
├── etcd_main.py                 # 测试服务是否正常
├── flask_test.py                # foo服务程序,注册
├── README.md
└── requirements.txt
```

## 一、确认软件安装

0. 更新软件库
```
sudo apt update
```

1. 安装docker
```
wget -qO- https://get.docker.com/ | sh
```

2. 安装etcd
```
sudo docker pull quay.io/coreos/etcd:latest
```

3. python使用python3.5
```
python3 --version
Python 3.5.3
```

4. 安装pip3

```
sudo apt-get install python3-pip
```

5. 更新pip3

```
sudo pip3 install --upgrade pip
```

## 二、安装和使用虚拟环境

- 安装虚拟环境管理工具

```
sudo pip3 install virtualenv
```

- 安装虚拟环境管理扩展包

```
sudo pip3 install virtualenvwrapper 
```

- 编辑家目录下面的.bashrc文件，添加下面几行。

```
if [ -f /usr/local/bin/virtualenvwrapper.sh ]; then
  export WORKON_HOME=$HOME/.virtualenvs
  export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
  source /usr/local/bin/virtualenvwrapper.sh
fi
```

- 使用以下命令使配置立即生效

```
source ~/.bashrc
```

- 创建虚拟环境命令(**需要连网**)：

```
# 创建python2虚拟环境：
mkvirtualenv 虚拟环境名

# 创建python3虚拟环境：
mkvirtualenv --python=/usr/bin/python3 etcd_test
```

- 进入虚拟环境工作：

```
workon 虚拟环境名
```

- 查看机器上有哪些虚拟环境：

```
workon
```

- 退出虚拟环境：

```
# 使失效
deactivate  
```

- 删除虚拟环境：

```
rmvirtualenv 虚拟环境名
```

## 三、Git安装与配置

1. 安装git

```
sudo apt-get install git
```

2. 设置git用户名和邮箱

```
git config --global user.name "Your Name"
git config --global user.email "youremail@example.com"
```

3. 生成ssh公私钥对

```
ssh-keygen -t rsa -C youremail@example.com
```

4. 将公钥id_rsa.pub内容拷贝一份到GitLab设置中的SSH Keys中

## 四、部署步骤

1. 在家目录下创建workspace文件夹

```
mkdir ~/workspace
cd ~/workspace
```

2. 克隆项目

```
git clone git@gitlab.using.site:zhangxf/etcd_test.git
```

3. 进入虚拟环境，根据不同的模块，安装相应的依赖包

```bash
cd etcd_test
workon etcd_test
pip install -r requirements.txt
```

## 五、平台运行

- 以3台机器为例，host分别为

```
172.16.81.1 node1
172.16.81.130 node2
172.16.81.129 node3
```

- 新建etcd 集群， 首先在新集群所有机器设置新集群环境变量

```
# 这些环境变量是为了方便理解，摘取出的一些命令行参数（所有机器统一使用）
export TOKEN=token-01
export CLUSTER_STATE=new
export NAME_1=node1
export NAME_2=node2
export HOST_1=172.16.81.1
export HOST_2=172.16.81.131
export CLUSTER=${NAME_1}=http://${HOST_1}:2380,${NAME_2}=http://${HOST_2}:2380,
```

在node1上执行
```
export THIS_NAME=${NAME_1}
export THIS_IP=${HOST_1}
sudo docker run -d --name ${THIS_NAME} \
    --net=host \
	  quay.io/coreos/etcd \
    etcd \
    --data-dir=/tmp/etcd-data --name ${THIS_NAME} \
    --initial-advertise-peer-urls http://${THIS_IP}:2380 --listen-peer-urls http://${THIS_IP}:2380 \
    --advertise-client-urls http://${THIS_IP}:2379 --listen-client-urls http://${THIS_IP}:2379 \
    --initial-cluster-state ${CLUSTER_STATE} \
    --initial-cluster-token ${TOKEN} \
    --initial-cluster ${CLUSTER}
```

node2
```
export THIS_NAME=${NAME_2}
export THIS_IP=${HOST_2}
sudo docker run -d --name ${THIS_NAME} \
    --net=host \
	  quay.io/coreos/etcd \
    etcd \
    --data-dir=/tmp/etcd-data --name ${THIS_NAME} \
    --initial-advertise-peer-urls http://${THIS_IP}:2380 --listen-peer-urls http://${THIS_IP}:2380 \
    --advertise-client-urls http://${THIS_IP}:2379 --listen-client-urls http://${THIS_IP}:2379 \
    --initial-cluster-state ${CLUSTER_STATE} \
    --initial-cluster-token ${TOKEN} \
    --initial-cluster ${CLUSTER}
```
docker run参数：
```
-d
  后台运行
--name=node1
  设置容器名
--restart=always
  容器停止时，自动重启容器
--net=host
  容器使用实体机ip
```

etcd 参数
```
-data-dir
  数据中心
--name
  节点名
--initial-advertise-peer-urls
  cluster所有节点的值（匹配initial-cluster）
--listen-peer-urls
  接受其他节点的同步请求
--advertise-client-urls
  客户端接口的地址
--listen-client-urls
  接受客户端请求
--initial-cluster-state
  集群状态（new or existing）
--initial-cluster-token
  集群id
--initial-cluster
  集群内所有机器
```

- 添加一个节点
首先在原集群使用命令添加新机器： 
```
# 这个是etcdctl的设置，使用v3接口，默认为v2接口
export ETCDCTL_API=3 
# 首先在原集群使用命令添加新机器： 
etcdctl --endpoints=172.16.81.1:2379 member add node3 --peer-urls=http://172.16.81.129:2380
```
然后启动新机器的etcd
```
export TOKEN=token-01
export CLUSTER_STATE=existing
export NAME_1=node1
export NAME_2=node2
export HOST_1=172.16.81.1
export HOST_2=172.16.81.131
export THIS_NAME=node3
export THIS_IP=172.16.81.129
export CLUSTER=${NAME_1}=http://${HOST_1}:2380,${NAME_2}=http://${HOST_2}:2380,${THIS_NAME}=http://${THIS_IP}:2380 

sudo docker run -d --name ${THIS_NAME} \
    --net=host \
	  quay.io/coreos/etcd \
    etcd \
    --data-dir=/tmp/etcd-data --name ${THIS_NAME} \
    --initial-advertise-peer-urls http://${THIS_IP}:2380 --listen-peer-urls http://${THIS_IP}:2380 \
    --advertise-client-urls http://${THIS_IP}:2379 --listen-client-urls http://${THIS_IP}:2379 \
    --initial-cluster-state ${CLUSTER_STATE} \
    --initial-cluster-token ${TOKEN} \
    --initial-cluster ${CLUSTER}
```

- 安装配置confd
将配置目录复制到/etc目录下
```
sudo cp confd /etcd -r
```
监听etcd的key value变化
```
confd -interval=10 -backend etcdv3 -node http://127.0.0.1:2379 &
```
confd参数
```
-interval 
  设置查询间隔
-backend 
  设置使用api版本（默认为v2）
-node
  设置集群node_ip
```
- 注册服务
在集群机器上使用flask_test程序测试服务注册
```
python flask_test.py
```
在客户端机器上使用etcd_main来测试服务的使用
```
python etcd_main.py
```

- discovery 建立集群， 可以使用托管在 discovery.etcd.io公共发现服务建立集群

```
# 获取一个集群大小为3的discovery URL
curl https://discovery.etcd.io/new?size=3
示例结果：https://discovery.etcd.io/e9fc43c1629948ce10349a703a10c3f8

# 在各个节点上启动
sudo docker run -d --name ${THIS_NAME} \
    --net=host \
	  quay.io/coreos/etcd \
    etcd \
    --data-dir=/tmp/etcd-data --name ${THIS_NAME} \
    --initial-advertise-peer-urls http://${THIS_IP}:2380 --listen-peer-urls http://${THIS_IP}:2380 \
    --advertise-client-urls http://${THIS_IP}:2379 --listen-client-urls http://${THIS_IP}:2379 \
	  --discovery https://discovery.etcd.io/e9fc43c1629948ce10349a703a10c3f8

```

发现服务协议帮助新的etcd成员使用共享发现URL发现集群引导阶段中的所有其他成员。

发现服务协议仅用于集群引导阶段，不能用于运行时重新配置或集群监视。

该协议使用新的发现令牌来引导一个唯一的 etcd集群。请记住，一个发现令牌只能代表一个etcd集群。只要此令牌上的发现协议启动，即使它中途失败，也不能用于引导另一个etcd集群。

如果discovery的地址使用https，则需要自己去搞证书，比较麻烦，改为http的就ok。另外如果启动集群失败了，discovery要重新生成，因为比如之前注册了node1，失败了再次启动，会报node1已经被注册。