# 项目概览: llm-deploy-project

本文档由`generate_project_overview.py`自动生成，包含了项目的结构树和所有可读文件的内容。

## 项目结构

```
llm-deploy-project/
├── tests
│   ├── aiotest.py
│   ├── client_demo.py
│   └── payload.json
├── .dockerignore
├── .gitignore
├── .python-version
├── Colab_manual.md
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

# 文件内容

## `.dockerignore`

```
# .dockerignore
.venv
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.env
vllm.log
```

## `.gitignore`

```
# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info

# Virtual environments
.venv

```

## `.python-version`

```
3.11

```

## `Colab_manual.md`

````text
这份 Colab 笔记本主要完成了以下几个核心任务：

挂载 Google Drive： 将您的 Google Drive 连接到 Colab 虚拟机，方便访问和保存项目文件。
安装和准备工具： 在全局环境中安装了快速包管理器 uv，并用它创建了一个包含 pip 的独立虚拟环境 (.venv)。
安装各种依赖。
启动 VLLM 服务： 使用虚拟环境中的 Python 解释器，在后台启动了 VLLM 的 OpenAI API 兼容服务，加载指定模型并监听端口，将输出重定向到日志文件。
创建公网 URL： 安装 pyngrok 库，获取 ngrok 认证 token，然后使用 ngrok 为本地运行的 VLLM 服务创建了一个公共访问地址。
./.venv/bin/pip install -e ".[gpu]" 为什么要安装各种依赖。这是因为 VLLM（以及大多数复杂的 Python 项目）并不是一个独立的、可以单独运行的文件。它依赖于许多其他的 Python 库和组件才能正常工作。

这些依赖项包括：
深度学习框架： VLLM 依赖于 PyTorch 等深度学习框架来执行模型的计算。
模型相关的库： 可能需要 Hugging Face 的 transformers、tokenizers 库来加载模型结构、权重和分词器。
高性能计算库： VLLM 依赖于 CUDA、cuBLAS、cuDNN 等 NVIDIA 提供的库来利用 GPU 的高性能计算能力。
其他辅助库： 可能还需要用于网络通信 (如 uvicorn, fastapi)、数据处理、并行计算等的库。
pyproject.toml 文件中定义了项目需要的所有这些依赖，而 ./.venv/bin/pip install -e ".[gpu]" 命令的作用就是读取这个文件，并在虚拟环境中自动下载、安装和配置所有这些 VLLM 正常运行所必需的依赖项。

特别是 ".[gpu]" 部分，它确保安装的是支持 GPU 的版本，因为 VLLM 的主要优势就是利用 GPU 进行高性能推理。

如果没有安装这些依赖，VLLM 的代码将无法找到它需要的组件，从而无法启动或正常工作，更不用说加载和运行大型语言模型了。所以这一步是启动 VLLM 服务的前提。

\# 1. 挂载 Google Drive
\`\`\`
from google.colab import drive
drive.mount('/content/drive')
\`\`\`

\# 2. 进入项目目录并检查文件
\`\`\`
%cd /content/drive/MyDrive/projects/llm-deploy-project
!ls -al
\`\`\`
\# 3. (最终精确修正版) 创建带 pip 的虚拟环境并在其中安装
\`\`\`
%%bash

\# 先安装最新版的 uv 到全局
pip install -q uv

\# 设置环境变量，避免跨文件系统警告
export UV_LINK_MODE=copy

\# 如果旧的 .venv 存在，先删掉，确保一个干净的开始
rm -rf .venv

\# 核心修正：使用 --seed 标志来创建包含 pip 的虚拟环境
uv venv --seed

\# 现在，./.venv/bin/pip 就会存在了
\# 使用它来安装依赖，确保所有包都100%安装在 .venv 中
./.venv/bin/pip install -e ".[gpu]"
\`\`\`

\# 3.5 (终极版) 验证 vllm 是否已在 .venv 中成功安装
\`\`\`
\# 直接调用 .venv 中的 pip list，结果绝对可靠
!./.venv/bin/pip list | grep vllm
\`\`\`

\# 4. (终极版) 使用 .venv 中的 Python 解释器启动服务
\`\`\`
\# 这是最明确、最不会出错的启动方式
!nohup ./.venv/bin/python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2-0.5B-Instruct \
    --trust-remote-code \
    --port 8000 > vllm.log 2>&1 &

\# 等待20秒让服务器有足够时间启动，然后查看日志
!sleep 20 && tail -n 20 vllm.log
\`\`\`

\# 5. (最终认证版) 使用 Authtoken 创建公网 URL
\`\`\`
\# 先在Colab的全局环境中安装 pyngrok
!pip install -q pyngrok

from google.colab import userdata
from pyngrok import ngrok

\# 注册ngrok账号并获取Authtoken，填入Colab环境变量中
\# 从 Colab Secrets 中获取我们存储的 Authtoken
NGROK_TOKEN = userdata.get('NGROK_AUTHTOKEN')

\# 设置 ngrok 的认证 token
ngrok.set_auth_token(NGROK_TOKEN)

\# 断开所有可能的旧隧道，确保干净的环境
ngrok.kill()

\# 连接到 8000 端口，创建新的隧道
public_url = ngrok.connect(8000)

print("✅ 服务隧道创建成功！")
print(f"你的公网URL是: {public_url}")
print("---")
print("请复制上面这个 https://开头的地址，填入你本地电脑的 .env 文件中！")
print("提醒：记得在URL末尾加上 /v1")
\`\`\`

\# 使用 asyncio.Semaphore 进行专业级并发控制
\`\`\`
import asyncio
import aiohttp
import json
import time
from collections import Counter

\# --- 配置参数 ---
URL = "http://localhost:8000/v1/chat/completions"
PAYLOAD_FILE = "tests/payload.json"
N_REQUESTS = 100  \# 我们增加总请求数，让测试在高并发下运行更长时间，数据更稳定
N_CONCURRENT = 55 \# 我们直接挑战之前测出最高QPS的并发数
\# -----------------

async def send_request(session, payload, headers):
    """发送一次请求并返回结果的底层函数"""
    start_time = time.monotonic()
    try:
        async with session.post(URL, json=payload, headers=headers) as response:
            await response.read()
            end_time = time.monotonic()
            return {
                "status": response.status,
                "time": end_time - start_time,
                "error": None
            }
    except Exception as e:
        end_time = time.monotonic()
        return {
            "status": -1,
            "time": end_time - start_time,
            "error": str(e)
        }

async def worker(semaphore, session, payload, headers):
    """
    这是一个带信号量控制的“工人”。
    它在执行真正的请求前后，会正确地获取和释放许可证。
    """
    async with semaphore:
        return await send_request(session, payload, headers)

async def main():
    """主函数，使用Semaphore来组织并发请求"""
    print("--- 开始使用 Python + Semaphore 进行专业级内部压力测试 ---")
    print(f"N_CONCURRENT = {N_CONCURRENT}")
    print(f"N_REQUESTS = {N_REQUESTS}")
    try:
        with open(PAYLOAD_FILE, 'r') as f:
            payload = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到 payload 文件 '{PAYLOAD_FILE}'")
        return

    headers = {'Content-Type': 'application/json'}
    
    \# 【核心修正】创建 Semaphore 对象
    semaphore = asyncio.Semaphore(N_CONCURRENT)
    
    tasks = []
    total_start_time = time.monotonic()
    
    async with aiohttp.ClientSession() as session:
        for _ in range(N_REQUESTS):
            \# 我们创建的是 worker 任务，而不是直接的 send_request 任务
            task = asyncio.create_task(worker(semaphore, session, payload, headers))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        
    total_end_time = time.monotonic()
    total_duration = total_end_time - total_start_time
    
    \# --- 结果分析和报告 (与之前相同) ---
    successes = [r for r in results if 200 <= r["status"] < 300]
    failures = [r for r in results if r["status"] >= 300 or r["status"] < 0]
    
    status_codes = Counter(r["status"] for r in results)
    errors = Counter(str(r["error"]) for r in failures if r["error"])

    print("\n--- 压测报告 (修正版) ---")
    print("Summary (摘要):")
    if results:
        success_rate = (len(successes) / len(results)) * 100
        requests_per_sec = len(results) / total_duration
        print(f"  Success rate (成功率): {success_rate:.2f}%")
        print(f"  Total (总耗时):        {total_duration:.4f} s")
        if successes:
            avg_time = sum(r["time"] for r in successes) / len(successes)
            fastest = min(r["time"] for r in successes)
            slowest = max(r["time"] for r in successes)
            print(f"  Slowest (最慢):      {slowest:.4f} s")
            print(f"  Fastest (最快):      {fastest:.4f} s")
            print(f"  Average (平均):      {avg_time:.4f} s")
        print(f"  Requests/sec (QPS): {requests_per_sec:.4f}")
    
    print("\nStatus code distribution (状态码分布):")
    for code, count in status_codes.items():
        label = "Client Error" if code == -1 else f"HTTP {code}"
        print(f"  [{label}] {count} responses")

    if errors:
        print("\nError distribution (错误分布):")
        for error, count in errors.items():
            print(f"  [{count}] {error}")

\# 运行主程序
asyncio.run(main())
\`\`\`
````

## `Dockerfile`

```dockerfile
# Dockerfile

# --- Stage 1: Builder ---
# 使用一个基础的Python镜像作为“构建环境”
# 我们的目标是在这个阶段安装好所有依赖，并打包成一个虚拟环境
FROM python:3.11-slim as builder

# 安装uv
RUN pip install uv

# 设置工作目录
WORKDIR /app

# 将依赖定义文件复制到镜像中
# 为了利用Docker的层缓存，我们先只复制这个文件
COPY pyproject.toml uv.lock ./

# 创建一个空的虚拟环境，这是最佳实践
RUN uv venv /opt/venv

# 核心步骤：使用uv在虚拟环境中安装所有依赖
# 注意：vLLM的安装非常耗时，但由于Docker的缓存机制，这一步只有在依赖变化时才会重新执行
RUN . /opt/venv/bin/activate && uv pip sync uv.lock

# --- Stage 2: Final Image ---
# 使用NVIDIA官方的CUDA镜像作为最终的“运行环境”
# 这个镜像体积更小，且包含了运行vLLM所需的所有GPU驱动和库
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# 设置一些环境变量，避免出现奇怪的提示
ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive

# 将我们在builder阶段创建好的、包含所有依赖的虚拟环境，完整地复制过来
COPY --from=builder /opt/venv /opt/venv

# 设置工作目录
WORKDIR /app

# 让Shell可以直接使用虚拟环境中的命令
ENV PATH="/opt/venv/bin:$PATH"

# 将我们项目的源代码复制到镜像中
COPY ./tests ./tests

# 暴露服务将要监听的端口
EXPOSE 8000

# 容器启动时要执行的默认命令
# 使用exec格式可以更好地处理信号
CMD [ \
    "python", \
    "-m", \
    "vllm.entrypoints.openai.api_server", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--model", "Qwen/Qwen2-0.5B-Instruct", \
    "--trust-remote-code" \
    ]
```

## `pyproject.toml`

```
[project]
name = "llm-deploy-project"
version = "0.1.0"
description = "A project to deploy LLM with vLLM and FastAPI"
authors = [{ name = "Jay Wei", email = "xiaofeng.0209@gmail.com" }]
readme = "README.md"
requires-python = ">=3.11, <3.12"

dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "python-dotenv",
    "openai",
    "aiohttp",
    "pyngrok", # 我们需要它在Colab里创建公网隧道
]

[project.optional-dependencies]
# 这里是只有在GPU环境（比如Colab）下才需要安装的重度依赖
gpu = [
    "vllm",
]

[tool.uv]
```

## `README.md`

````text

##\# **生产环境部署实战手册 (从Colab到云服务器)**

假设你已经购买了一台带有NVIDIA GPU的云服务器（例如 AWS EC2, GCP Compute Engine, AutoDL），并获得了公网IP地址。操作系统推荐使用 **Ubuntu 22.04 LTS**。

###\# **阶段一：服务器初始化与环境准备**

这一阶段的目标是配置一个干净、安全、满足vLLM运行要求的基础环境。

**1. 安全连接服务器**
   - **摒弃密码登录，使用SSH密钥**：这是生产环境安全的第一道防线。
   - **操作**：
     - 在你本地电脑生成SSH密钥对。
     - 将公钥 (`id_rsa.pub`) 添加到云服务器的 `~/.ssh/authorized_keys` 文件中。
     - 现在你可以通过 `ssh <your_username>@<your_server_ip>` 免密登录。

**2. 安装NVIDIA驱动和CUDA Toolkit**
   - vLLM的性能完全依赖于此。这是最关键的一步。
   - **操作**：
     - SSH登录到服务器后，遵循服务器提供商的官方文档或NVIDIA官方指南安装最新的驱动和CUDA。
     - **验证安装**：运行 `nvidia-smi` 命令。如果能看到GPU信息、驱动版本和CUDA版本，则表示安装成功。

     \`\`\`bash
     \# 在云服务器上执行
     nvidia-smi
     \`\`\`

**3. 安装项目管理工具 (Git & uv)**
   - **摒弃手动上传/Google Drive同步，使用Git**：代码版本管理是专业开发的基石。
   - **操作**：

     \`\`\`bash
     \# 在云服务器上执行
     \# 更新包列表
     sudo apt update

     \# 安装git
     sudo apt install git -y

     \# 安装uv (与Colab中类似)
     curl -LsSf https://astral.sh/uv/install.sh | sh
     source $HOME/.cargo/env
     \`\`\`

###\# **阶段二：项目部署与环境配置**

这一阶段，我们将把你的代码规范地部署到服务器上，并创建独立的运行环境。

**1. 克隆项目代码**
   - 首先，你需要将你的 `llm-deploy-project` 项目上传到一个Git仓库（如 GitHub, GitLab）。
   - **操作**：

     \`\`\`bash
     \# 在云服务器上执行
     \# 从你的仓库克隆项目
     git clone https://github.com/<your_username>/llm-deploy-project.git

     \# 进入项目目录
     cd llm-deploy-project
     \`\`\`

**2. 创建并配置Python虚拟环境**
   - 这一步与Colab类似，但现在是在一个持久化的文件系统上。
   - **操作**：
     \`\`\`bash
     \# 在云服务器的项目根目录下执行
     \# 创建带pip的虚拟环境
     uv venv --seed

     \# 激活环境 (注意：为方便后续操作，记住这个路径)
     \# source .venv/bin/activate
     
     \# 使用uv安装核心依赖
     \# 对于生产部署，我们直接安装vllm包，而不是从源码安装
     ./.venv/bin/uv add vllm==0.5.1 openai python-dotenv
     \# 注意：这里我们直接指定了包名，而不是`pip install -e ".[gpu]"`
     \# 这是因为我们是“使用”vLLM，而不是“开发”vLLM
     \`\`\`

**3. 创建`.env`配置文件**
   - 在服务器上，也需要一个`.env`文件，但`API_BASE_URL`会有所不同。
   - **操作**：
     - 在`llm-deploy-project`目录下创建`.env`文件，内容如下：

       \`\`\`
       \# .env on Server
       \# 在服务器上，我们通常监听所有地址
       VLLM_HOST="0.0.0.0" 
       VLLM_PORT="8000"
       MODEL_NAME="Qwen/Qwen2-0.5B-Instruct"
       \`\`\`

###\# **阶段三：服务的专业化管理与启动**

这是与Colab **最核心的区别**。我们将摒弃 `nohup`，使用Linux标准的进程守护系统 `systemd` 来管理我们的服务。

**为什么用 `systemd` 而不是 `nohup`?**
*   **自动重启**：如果服务因任何原因崩溃，`systemd` 会自动将其拉起。
*   **开机自启**：可以配置服务器重启后，服务自动运行。
*   **标准化管理**：使用 `systemctl` 命令可以统一管理（启动、停止、重启、查看状态）。
*   **日志集中管理**：日志会由 `journald` 统一收集，可以通过 `journalctl` 查看，更强大、更规范。

**1. 创建 `systemd` 服务文件**
   - **操作**：

     \`\`\`bash
     \# 在云服务器上执行
     \# 使用nano或vim创建一个新的服务配置文件
     sudo nano /etc/systemd/system/vllm.service
     \`\`\`

   - 将以下内容粘贴到文件中。**请务必将 `User` 和 `WorkingDirectory`/`ExecStart` 中的路径修改为你自己的用户名和项目路径！**

     \`\`\`ini
     [Unit]
     Description=VLLM OpenAI-Compatible API Service
     After=network.target

     [Service]
     \# 替换为你的用户名
     User=ubuntu
     \# 替换为你的项目根目录的绝对路径
     WorkingDirectory=/home/ubuntu/llm-deploy-project
     
     \# 启动命令的核心
     \# 注意这里使用了.venv中的python解释器的绝对路径
     ExecStart=/home/ubuntu/llm-deploy-project/.venv/bin/python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2-0.5B-Instruct --trust-remote-code --host 0.0.0.0 --port 8000
     
     \# 确保vLLM能找到CUDA
     Environment="HOME=/home/ubuntu"
     
     \# 失败时自动重启
     Restart=always
     RestartSec=10

     [Install]
     WantedBy=multi-user.target
     \`\`\`

**2. 管理 `vllm` 服务**
   - **操作**：

     \`\`\`bash
     \# 在云服务器上执行
     \# 1. 重新加载systemd配置，使其识别新服务
     sudo systemctl daemon-reload

     \# 2. 启动vllm服务
     sudo systemctl start vllm

     \# 3. (可选，但推荐) 设置服务开机自启
     sudo systemctl enable vllm

     \# 4. 查看服务状态，确保它正在运行 (active (running))
     sudo systemctl status vllm
     \`\`\`
     - 如果状态不是 `active (running)`，可以使用 `sudo journalctl -u vllm -f` 查看实时日志来排查错误。

###\# **阶段四：公网访问与压力测试**

现在你的服务已经在云端稳定运行，不再需要`ngrok`这种内网穿透工具了。

**1. 配置防火墙/安全组**
   - **摒弃 `ngrok`，使用云服务商的安全组**：这是控制公网访问的标准做法。
   - **操作**：
     - 登录你的云服务商控制台。
     - 找到你的服务器实例对应的“安全组”或“防火墙”规则。
     - **添加入站规则**：允许来自任何源 (`0.0.0.0/0`) 的 TCP 流量访问端口 `8000`。

**2. 在本地进行压力测试**
   - **操作**：
     - 回到你的**本地笔记本电脑**。
     - 打开 `llm-deploy-project` 项目中的 `.env` 文件。
     - **修改 `API_BASE_URL`**，将 `ngrok` 的地址换成你云服务器的公网IP。

       \`\`\`
       \# .env on your Local Laptop
       MODEL_NAME="Qwen/Qwen2-0.5B-Instruct"
       API_BASE_URL="http://<你的云服务器公网IP>:8000/v1"
       API_KEY="not-needed"
       \`\`\`
     - 现在，你可以在本地直接运行你的 `client_demo.py` 和 **专业级并发压测脚本**了！

       \`\`\`bash
       \# 在本地笔记本上运行
       uv run python tests/your_async_benchmark.py
       \`\`\`
**3. 实时监控GPU**
   - 当你在本地进行压测时，可以同时在服务器上打开另一个SSH窗口，实时观察GPU的使用情况。

     \`\`\`bash
     \# 在云服务器上执行，每秒刷新一次
     watch -n 1 nvidia-smi
     \`\`\`
   - 你会看到 `GPU-Util` (GPU利用率) 和 `Memory-Usage` (显存占用) 在压测期间飙升，这证明你的服务正在火力全开地处理请求。

##\# **总结：从 Colab 到生产的跃迁**

| 特性 | Colab (实验环境) | 云服务器 (生产环境) | 转变的意义 |
| :--- | :--- | :--- | :--- |
| **代码来源** | Google Drive / 手动上传 | Git 仓库 (`git clone`) | **版本控制**，团队协作，可追溯 |
| **公网访问** | `ngrok` 内网穿透 | **公网IP + 安全组/防火墙** | **稳定、安全**，企业级网络架构 |
| **服务管理** | `nohup ... &` | **`systemd` 服务** | **高可用**，自动重启，标准化运维 |
| **环境管理** | 临时虚拟机 | 持久化服务器 + `uv venv` | **一致性、可复现**的环境 |
| **安全性** | 较低（依赖Colab） | **SSH密钥 + 严格防火墙** | **生产安全**的基石 |

通过以上步骤，你不仅部署了服务，更是建立了一套**可维护、可扩展、稳定可靠**的生产部署流程。现在，当面试官再次问你如何从0部署大模型时，你可以自信地、条理清晰地阐述以上整套方案。

如果还有任何疑问，或者想继续探索如**Docker容器化部署**等更高级的主题，随时告诉我！
````

## `tests/aiotest.py`

```python
import asyncio
import aiohttp
import json
import time
from collections import Counter
import os
from dotenv import load_dotenv

# 在脚本开头加载环境变量
load_dotenv()
API_KEY = os.getenv("API_KEY")

# --- 配置参数 ---
URL = "http://localhost:8000/v1/chat/completions"
PAYLOAD_FILE = "payload.json"
N_REQUESTS = 100  # 我们增加总请求数，让测试在高并发下运行更长时间，数据更稳定
N_CONCURRENT = 55 # 我们直接挑战之前测出最高QPS的并发数
# -----------------

async def send_request(session, payload, headers):
    """发送一次请求并返回结果的底层函数"""
    start_time = time.monotonic()
    try:
        async with session.post(URL, json=payload, headers=headers) as response:
            await response.read()
            end_time = time.monotonic()
            return {
                "status": response.status,
                "time": end_time - start_time,
                "error": None
            }
    except Exception as e:
        end_time = time.monotonic()
        return {
            "status": -1,
            "time": end_time - start_time,
            "error": str(e)
        }

async def worker(semaphore, session, payload, headers):
    """
    这是一个带信号量控制的“工人”。
    它在执行真正的请求前后，会正确地获取和释放许可证。
    """
    async with semaphore:
        return await send_request(session, payload, headers)

async def main():
    """主函数，使用Semaphore来组织并发请求"""
    print("--- 开始使用 Python + Semaphore 进行专业级内部压力测试 ---")
    print(f"N_CONCURRENT = {N_CONCURRENT}")
    print(f"N_REQUESTS = {N_REQUESTS}")
    try:
        with open(PAYLOAD_FILE, 'r') as f:
            payload = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到 payload 文件 '{PAYLOAD_FILE}'")
        return

    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {API_KEY}'}
    
    # 【核心修正】创建 Semaphore 对象
    semaphore = asyncio.Semaphore(N_CONCURRENT)
    
    tasks = []
    total_start_time = time.monotonic()
    
    async with aiohttp.ClientSession() as session:
        for _ in range(N_REQUESTS):
            # 我们创建的是 worker 任务，而不是直接的 send_request 任务
            task = asyncio.create_task(worker(semaphore, session, payload, headers))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        
    total_end_time = time.monotonic()
    total_duration = total_end_time - total_start_time
    
    # --- 结果分析和报告 (与之前相同) ---
    successes = [r for r in results if 200 <= r["status"] < 300]
    failures = [r for r in results if r["status"] >= 300 or r["status"] < 0]
    
    status_codes = Counter(r["status"] for r in results)
    errors = Counter(str(r["error"]) for r in failures if r["error"])

    print("\n--- 压测报告 (修正版) ---")
    print("Summary (摘要):")
    if results:
        success_rate = (len(successes) / len(results)) * 100
        requests_per_sec = len(results) / total_duration
        print(f"  Success rate (成功率): {success_rate:.2f}%")
        print(f"  Total (总耗时):        {total_duration:.4f} s")
        if successes:
            avg_time = sum(r["time"] for r in successes) / len(successes)
            fastest = min(r["time"] for r in successes)
            slowest = max(r["time"] for r in successes)
            print(f"  Slowest (最慢):      {slowest:.4f} s")
            print(f"  Fastest (最快):      {fastest:.4f} s")
            print(f"  Average (平均):      {avg_time:.4f} s")
        print(f"  Requests/sec (QPS): {requests_per_sec:.4f}")
    
    print("\nStatus code distribution (状态码分布):")
    for code, count in status_codes.items():
        label = "Client Error" if code == -1 else f"HTTP {code}"
        print(f"  [{label}] {count} responses")

    if errors:
        print("\nError distribution (错误分布):")
        for error, count in errors.items():
            print(f"  [{count}] {error}")

# 运行主程序
asyncio.run(main())
```

## `tests/client_demo.py`

```python
# tests/client_demo.py
import os
import asyncio
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME")
API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

def simple_chat():
    """演示一个简单的同步聊天请求。"""
    print("--- 简单同步聊天测试 ---")
    client = OpenAI(api_key=API_KEY,base_url=API_BASE_URL,)
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "system","content": "你是一个乐于助人的AI助手。",},
            {"role": "user","content": "你好，请介绍马来西亚。",}],
        model=MODEL_NAME,
        max_tokens=256,
    )
    
    print("AI助手的回复:")
    print(chat_completion.choices[0].message.content)
    print("\n" + "-" * 20)

def streaming_chat():
    """演示流式输出的聊天请求。"""
    print("\n--- 流式同步聊天测试 ---")
    client = OpenAI(api_key=API_KEY,base_url=API_BASE_URL,)
    
    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "请给我讲一个关于程序员的笑话"}],
        stream=True,
        max_tokens=256,
    )
    
    print("AI助手的回复 (流式):")
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end='', flush=True)
    print("\n" + "-" * 20)

async def async_stream_main():
    print(f"--- 流式异步聊天测试 ---")
    client = AsyncOpenAI(api_key=API_KEY, base_url=API_BASE_URL)
    
    stream = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "你好，介绍北美十三州"}],
        stream=True,
        max_tokens=256,
    )
    
    print("AI助手的回复 (异步流式):")
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end='', flush=True)
    print("\n" + "-" * 20)

if __name__ == "__main__":
    if not API_BASE_URL or "<YOUR_NGROK_PUBLIC_URL_HERE>" in API_BASE_URL:
        print("错误: 请先在 .env 文件中设置你的 API_BASE_URL!")
    else:
        simple_chat()
        streaming_chat()
        asyncio.run(async_stream_main())
        
```

## `tests/payload.json`

```json
{
  "model": "Qwen/Qwen2-0.5B-Instruct",
  "messages": [
    {"role": "user", "content": "用一句话描述什么是人工智能"}
  ],
  "temperature": 0.7,
  "max_tokens": 50
}
```

