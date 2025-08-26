# LLM 高并发服务部署项目 (llm-deploy-project)

[![Python Version](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Docker](https://img.shields.io/badge/Docker-Powered-blue.svg)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-green.svg)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 项目概览

本项目是一个端到端的、生产级的解决方案，旨在演示如何从零开始，将一个开源大语言模型（以 `Qwen/Qwen2-0.5B-Instruct` 为例）部署为稳定、安全、高并发的API服务。

该项目完整覆盖了从本地开发测试、手动服务器部署，到最终实现全自动化CI/CD的每一个关键环节，是展示现代MLOps/DevOps实践能力的绝佳范例。

## ✨ 核心特性

- **高性能推理**: 使用业界领先的 **vLLM** 推理引擎，通过PagedAttention等技术实现高吞吐量、低延迟的模型服务。
- **标准化API**: 提供与 **OpenAI API** 完全兼容的接口，无缝对接现有生态。
- **安全认证**: 通过 **API Key** 对服务进行保护，防止未经授权的访问。
- **容器化部署**: 使用 **Docker** 将服务打包成标准、可移植的镜像，实现环境一致性与快速部署。
- **自动化CI/CD**: 配置 **GitHub Actions** 实现从代码推送到线上部署的全自动化流程，无需手动干预。
- **专业化工具链**: 采用 `uv` 进行高速环境与依赖管理，遵循PEP标准。
- **性能压测**: 包含基于 `asyncio` 的高并发压力测试脚本，用于验证和评估服务性能。

## 🔧 技术栈

- **模型推理**: `vLLM`
- **Python版本**: `3.11`
- **依赖管理**: `uv`
- **容器化**: `Docker` & `NVIDIA Container Toolkit`
- **CI/CD**: `GitHub Actions`
- **云服务器**: 任何支持GPU的Linux服务器 (e.g., Ubuntu 22.04)

---

## 🏁 快速开始 (本地客户端测试)

在对服务进行部署之前，你可以在本地配置客户端环境，以便与部署在云端的服务进行交互和测试。

### 1. 环境准备

- 安装 [Git](https://git-scm.com/)
- 安装 [Python 3.11](https://www.python.org/)
- 安装 [uv](https://github.com/astral-sh/uv): `pip install uv`

### 2. 克隆并安装依赖

```bash
# 1. 克隆项目
git clone https://github.com/<your_username>/llm-deploy-project.git
cd llm-deploy-project

# 2. 使用uv创建并激活虚拟环境
uv venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

# 3. 安装所有依赖
uv sync
```

### 3. 配置环境变量

在项目根目录创建一个 `.env` 文件。你可以从 `.env.example` (如果提供) 复制或手动创建，并填入你的服务信息：

```env
# .env
MODEL_NAME="Qwen/Qwen2-0.5B-Instruct"
API_BASE_URL="http://<你的云服务器公网IP>:8000/v1"
API_KEY="your-secret-key-here"
```

### 4. 运行客户端与压测

```bash
# 运行功能演示客户端
uv run python tests/client_demo.py

# 运行高并发压力测试
uv run python tests/aiotest.py
```

---

## ☁️ 部署指南

我们提供两种部署方式：手动的Docker部署（用于理解过程）和全自动的CI/CD部署（推荐的生产实践）。

### 部署方式一：手动Docker部署 (推荐)

这是在服务器上部署服务的核心方法。

#### 1. 服务器环境准备

- 一台带有NVIDIA GPU的云服务器 (Ubuntu 22.04 LTS 推荐)。
- 安装最新的NVIDIA驱动和CUDA Toolkit。
- 安装Docker和NVIDIA Container Toolkit (请参考官方文档)。

#### 2. 构建并运行镜像

SSH登录到你的服务器，执行以下步骤：

```bash
# 1. 克隆项目
git clone https://github.com/<your_username>/llm-deploy-project.git
cd llm-deploy-project

# 2. 使用Docker构建镜像
# -t 参数为你的镜像命名: <image_name>:<tag>
docker build -t qwen-vllm-service:1.0 .

# 3. 运行容器
# 记得替换 your-secret-key-here 为你的真实API Key
docker run -d \
    --gpus all \
    -p 8000:8000 \
    --name qwen-server \
    --restart always \
    qwen-vllm-service:1.0 \
    --api-key "your-secret-key-here"
```

**命令解析**:
- `-d`: 后台运行。
- `--gpus all`: 将所有GPU挂载到容器中，**vLLM运行的必需项**。
- `-p 8000:8000`: 将服务器的8000端口映射到容器的8000端口。
- `--name qwen-server`: 为容器命名，方便管理。
- `--restart always`: 容器退出时自动重启，保证服务高可用。

#### 4. 管理服务

```bash
# 查看正在运行的容器
docker ps

# 查看实时日志
docker logs -f qwen-server

# 停止服务
docker stop qwen-server

# 删除容器
docker rm qwen-server
```

### 部署方式二：全自动化CI/CD (基于GitHub Actions)

这是最先进的部署方式。在你完成一次性配置后，每次 `git push` 到 `main` 分支都会自动触发部署。

#### 1. 准备工作

- 一个 [Docker Hub](https://hub.docker.com/) 账号。
- 服务器已按 **部署方式一** 中的要求准备好基础环境。

#### 2. 配置GitHub Secrets

进入你的GitHub项目仓库 -> `Settings` -> `Secrets and variables` -> `Actions`，添加以下 **Repository secrets**：

| Secret 名称        | 描述                                                           |
| ------------------ | -------------------------------------------------------------- |
| `DOCKERHUB_USERNAME` | 你的Docker Hub用户名。                                         |
| `DOCKERHUB_TOKEN`  | 用于登录Docker Hub的访问令牌 (在Docker Hub安全设置中创建)。    |
| `SERVER_HOST`      | 你的云服务器公网IP地址。                                       |
| `SERVER_USERNAME`  | SSH登录服务器所用的用户名 (e.g., `ubuntu`)。                     |
| `SERVER_SSH_KEY`   | 用于免密登录服务器的SSH**私钥**的完整内容。                      |
| `VLLM_API_KEY`     | 你为vLLM服务设置的API密钥。                                    |


#### 3. 触发部署

将你的代码（包括 `.github/workflows/deploy.yml` 文件）推送到GitHub仓库的`main`分支。

```bash
git push origin main
```

之后，你可以在GitHub仓库的 `Actions` 标签页中实时观察自动构建、推送和部署的全过程。

## 📂 项目结构

```
llm-deploy-project/
├── .github/workflows
│   └── deploy.yml        # CI/CD 工作流定义
├── tests
│   ├── aiotest.py        # 异步高并发压测脚本
│   ├── client_demo.py    # 功能演示客户端
│   └── payload.json      # API请求体示例
├── .dockerignore         # 定义Docker构建时忽略的文件
├── .gitignore            # 定义Git忽略的文件
├── .python-version       # 指定项目使用的Python版本
├── Dockerfile            # 容器镜像构建蓝图 (多阶段构建)
├── pyproject.toml        # 项目元数据与依赖定义 (PEP 621)
├── README.md             # 项目说明文档
└── uv.lock               # 精确锁定所有依赖版本，保证环境可复现
```

## 💡 未来可扩展方向

- **部署到Kubernetes**: 将服务封装为Helm Chart，实现云原生部署、弹性伸缩和滚动更新。
- **服务监控与告警**: 集成Prometheus和Grafana，对服务的QPS、延迟、GPU利用率等关键指标进行监控。
- **日志中心化**: 使用ELK Stack或Loki，将服务日志统一收集和管理，便于问题排查。
- **模型优化**: 探索AWQ、GPTQ等更高级的量化技术，进一步提升推理性能。