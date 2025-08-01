# Flyte Tasks 脚本

本目录包含用于处理 Flyte 任务的脚本。

## 安装

在运行任何脚本之前，请确保已安装所需的依赖项：

```bash
# 在 Linux/Mac 上
./script/install.sh

# 在 Windows 上
pip install flytekit
pip install flytekitplugins-flyteinteractive
```

## 脚本说明

### 1. run_ide.py

此脚本执行 `ide.py` 任务并捕获 VSCode 访问 URL。

#### 使用方法

```bash
# 在 Linux/Mac 上
python3 script/run_ide.py

# 在 Windows 上
python script/run_ide.py
```

#### 功能说明

1. 执行 `tasks` 目录中的 `ide.py` 脚本
2. 捕获执行输出
3. 从输出中提取 VSCode 访问 URL
4. 向用户显示 URL

如果脚本无法在输出中找到 VSCode URL，它将显示错误消息并显示完整输出以供调试。

#### 输出示例

```
Executing /path/to/flyte-tasks/tasks/ide.py...

Output from ide.py:
forward
backward
... (其他输出) ...
VSCode instance is available at: https://example.com/vscode/12345

==================================================
VSCode access URL: https://example.com/vscode/12345
==================================================
```

### 2. run.sh

此脚本使用 `pyflyte` 命令远程运行 `ide.py` 中的工作流。

#### 使用方法

```bash
# 在 Linux/Mac 上
./tasks/run.sh

# 在 Windows 上
cd tasks
pyflyte run --remote ide.py wf_train
```

### 3. pull.sh

此脚本用于拉取 IDE 任务所需的 Docker 镜像。

#### 使用方法

```bash
# 在 Linux/Mac 上
./script/pull.sh

# 在 Windows 上
crictl pull ghcr.fzyun.io/flyteorg/flytekit:flyteinteractive-latest
```

### 4. port-forward.sh

此脚本用于设置端口转发，以便访问远程运行的 VSCode 实例。

#### 使用方法

```bash
# 在 Linux/Mac 上
./script/port-forward.sh

# 在 Windows 上
kubectl port-forward --address 0.0.0.0 ap24d29gfbbdhjnsp5wc-n0-0 8080:8080 -n flytesnacks-development
```

## 完整工作流程

1. 安装依赖项（使用 install.sh 或手动安装）
2. 拉取所需的 Docker 镜像（使用 pull.sh）
3. 运行 IDE 任务：
   - 本地运行：使用 run_ide.py
   - 远程运行：使用 run.sh
4. 如果远程运行，设置端口转发（使用 port-forward.sh）
5. 使用生成的 URL 访问 VSCode 实例

## 故障排除

如果遇到任何问题：

1. 确保已安装所有必需的依赖项
2. 检查脚本显示的完整输出中是否有任何错误消息
3. 验证 `ide.py` 是否能够单独正确执行
4. 如果未检测到 URL，请检查输出中 URL 的格式，并在必要时更新 `run_ide.py` 中的正则表达式模式
5. 确保 Docker 镜像已正确拉取
6. 检查 Kubernetes 集群连接和命名空间配置是否正确