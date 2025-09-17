# python指令
## python加速源

### 清华源
```shell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package
```

### 阿里源
```shell
pip install -i https://mirrors.aliyun.com/pypi/simple some-package
```

## uv命令操作
### 安装
```shell
Linux / MacOS：
curl -LsSf https://astral.sh/uv/install.sh | sh
Windows：
powershell -ExecutionPolicy ByPass -c 'irm https://astral.sh/uv/install.ps1 | iex'

# 若后续无法使用，请添加环境变量
[Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\Users\hujianfei\.local\bin", "User")
```

### 使用
```shell
# 1. 进入项目目录
cd myproject
# 2. 创建并激活虚拟环境
uv venv --python 3.11    # 速度极慢
# 替代方案
uv venv .venv -p C:\Users\gail_dev\python-sdk\python3.12.9\python.exe
source .venv/bin/activate   # Win: .venv\Scripts\activate
# 3. 安装依赖
uv pip install -r requirements.txt
uv pip install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
# 4. 开发中安装新包
uv pip install pytest pytest-cov
# 5. 生成锁文件（可选）
uv pip freeze > requirements-lock.txt
# 6. 完成后退出
deactivate
```

Proxy start
```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.11
source .venv/bin/activate
uv pip install flask requests flask-cors
python ollama_proxy.py
```
### nvm命令安装
github下载，自行安装

**使用 `wget`：**
```shell
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash


source ~/.bashrc
或
source ~/.profile
```

# Docker
```shell
win11安装docker
1. 升级或安装wsl
wsl --install
wsl --update
# 如果升级失败，提示，连接断开，可以尝试下面命令
wsl --update --web-download
2. 启用hyperv
dism /online /enable-feature /featurename:Microsoft-Hyper-V-All /all /norestart
dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism /online /enable-feature /featurename:HypervisorPlatform /all /norestart
bcdedit /set hypervisorlaunchtype auto
3. 安装docker-desktop
```


## docker第三方仓库
```shell
docker login --username=username my-dns-name.cn-beijing.personal.cr.aliyuncs.com
pwd:123123

docker tag 4c23edde3f79 crpi-gdv18d1dala6mkcc.cn-beijing.personal.cr.aliyuncs.com/xal-ai/dify:dify-api-1.8
docker push crpi-gdv18d1dala6mkcc.cn-beijing.personal.cr.aliyuncs.com/xal-ai/dify:dify-api-1.8
```


## 1panel Docker 
### 安装ES
```shell
创建存储卷（持久化数据）
暂时无法在飞书文档外展示此内容
暴露端口
9200
9300
环境变量配置
暂时无法在飞书文档外展示此内容

注意：若开启 xpack.security.enabled=true，还需添加 ELASTIC_PASSWORD 变量设置管理员密码（如 ELASTIC_PASSWORD=YourStrongPassword123!）。
```
### 安装Kibana
```shell
拉取镜像
docker pull docker.1ms.run/kibana:8.18.0
暴露端口
5601
环境变量配置
ELASTICSEARCH_HOSTS=["http://127.0.0.1:9200"]
ELASTICSEARCH_SSL_VERIFICATIONMODE=none
PATH=/usr/share/kibana/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ELASTIC_CONTAINER=true
```