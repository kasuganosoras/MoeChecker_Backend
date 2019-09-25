# MoeChecker_Backend
Moe Checker 后端程序，使用 Python 编写，需要 Python 3.6+

Ping 部分源码是从 CSDN 找的，因为时间太久远找不到作者了。

## 安装方法

首先准备一个 Linux 服务器，需要 Root 权限（因为需要发送 RawSocket 数据包，只有 root 权限用户才能发送）。

然后将项目 clone 到本地

```
git clone https://github.com/kasuganosoras/MoeChecker_Backend
```

安装好 Python 3.6、Screen

```
yum install python36 python36-pip screen -y
pip3 install requests
```

运行后端程序

```
screen -S moechecker
# 如果是国外服务器请运行 backend2.py
python3 backend.py
```

浏览器访问 http://你的IP地址:1012/ 查看是否显示 400 Bad Request，如果是的话就说明正常了。

请将您的服务器 IP 地址和名字发送到 akkariins#gmail.com（# 换成 @），我就会将它加入到测速列表中。

> *名字可自定义，比如 “江苏宿迁电信”、“美国洛杉矶”*

## 开源协议

本项目使用 GPL v3 协议开源
