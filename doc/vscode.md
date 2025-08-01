# FlyteInteractive VSCode Decorator

*FlyteInteractive VSCode 装饰器*

## Overview

*`@vscode` 只需更改一行即可将 Python 任务转换为 Visual Studio Code 服务器，从而实现远程环境中的连接和调试。*

## Import

```python
from flytekit import task, workflow
from flytekitplugins.flyteinteractive import vscode
```

## Usage


*将 `@vscode` 装饰器添加到任务函数定义中：*

```
from flytekit import task, workflow,Resources
from flytekitplugins.flyteinteractive import vscode


@task(
    container_image="ghcr.io/flyteorg/flytekit:flyteinteractive-latest",
    requests=Resources(cpu="1", mem="2000Mi"),
)

@vscode
def train():
    print("forward")
    print("backward")


@workflow
def wf_train():
    train()


if __name__ == "__main__":
    wf_train()
```

## How It Works

*`@vscode` 装饰器在运行时会将任务转换为 Visual Studio Code 服务器。此过程会覆盖任务函数体的标准执行，并启动一个命令来启动 Visual Studio Code 服务器。*


## 使用 VSCode 预构建 Docker 镜像
*为了避免在运行时下载 VSCode 和扩展，可以将它们预先构建到 Docker 镜像中，从而加速设置。*

```
# Include this line if `curl` isn't installed in the image.
RUN apt-get -y install curl
Download and extract VSCode.
RUN mkdir -p /tmp/code-server
RUN curl -kfL -o /tmp/code-server/code-server-4.18.0-linux-amd64.tar.gz https://github.com/coder/code-server/releases/download/v4.18.0/code-server-4.18.0-linux-amd64.tar.gz
RUN tar -xzf /tmp/code-server/code-server-4.18.0-linux-amd64.tar.gz -C /tmp/code-server/
ENV PATH="/tmp/code-server/code-server-4.18.0-linux-amd64/bin:${PATH}"
# TODO: download and install extensions
```