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