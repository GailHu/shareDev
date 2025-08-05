# 使用CentOS作为基础镜像
FROM ubuntu:22.04

# 设置环境变量
ENV JAVA_HOME=/usr/lib/jvm/jdk-21.0.7
ENV MAVEN_HOME=/usr/local/apache-maven
ENV PATH=$PATH:$JAVA_HOME/bin:$MAVEN_HOME/bin:/usr/local/mysql/bin:/usr/local/bin:/root/.local/bin

# 更新系统并安装基础工具  
RUN apt-get update && \
    apt-get install -y wget tar gzip unzip vim net-tools curl sudo software-properties-common openssh-server git-lfs && \
    apt-get clean

# 安装JDK 21
RUN wget https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.tar.gz && \
    mkdir -p /usr/lib/jvm/ && \
    tar -zxvf jdk-21_linux-x64_bin.tar.gz -C /usr/lib/jvm/ && \
    rm jdk-21_linux-x64_bin.tar.gz && \
    update-alternatives --install /usr/bin/java java $JAVA_HOME/bin/java 20000 && \
    update-alternatives --install /usr/bin/javac javac $JAVA_HOME/bin/javac 20000

# 安装Maven
RUN wget https://dlcdn.apache.org/maven/maven-3/3.9.10/binaries/apache-maven-3.9.10-bin.tar.gz && \
    tar -zxvf apache-maven-3.9.10-bin.tar.gz -C /usr/local/ && \
    mv /usr/local/apache-maven-3.9.10 /usr/local/apache-maven && \
    rm apache-maven-3.9.10-bin.tar.gz
 
# 安装 code-server 和 vscode 常用插件
RUN curl -fsSL https://code-server.dev/install.sh | sh \
  && code-server --install-extension redhat.vscode-yaml \
  && code-server --install-extension detachhead.basedpyright \
  && code-server --install-extension tamasfe.even-better-toml \
  && code-server --install-extension ygqygq2.turbo-file-header \
  && code-server --install-extension tencent-cloud.coding-copilot \
  && code-server --install-extension eamodio.gitlens \
  && code-server --install-extension ms-python.python \
  && code-server --install-extension ms-toolsai.jupyter \
  && echo done

# 指定字符集支持命令行输入中文（根据需要选择字符集）
ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8