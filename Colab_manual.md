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

# 1. 挂载 Google Drive
```
from google.colab import drive
drive.mount('/content/drive')
```

# 2. 进入项目目录并检查文件
```
%cd /content/drive/MyDrive/projects/llm-deploy-project
!ls -al
```
# 3. (最终精确修正版) 创建带 pip 的虚拟环境并在其中安装
```
%%bash

# 先安装最新版的 uv 到全局
pip install -q uv

# 设置环境变量，避免跨文件系统警告
export UV_LINK_MODE=copy

# 如果旧的 .venv 存在，先删掉，确保一个干净的开始
rm -rf .venv

# 核心修正：使用 --seed 标志来创建包含 pip 的虚拟环境
uv venv --seed

# 现在，./.venv/bin/pip 就会存在了
# 使用它来安装依赖，确保所有包都100%安装在 .venv 中
./.venv/bin/pip install -e ".[gpu]"
```

# 3.5 (终极版) 验证 vllm 是否已在 .venv 中成功安装
```
# 直接调用 .venv 中的 pip list，结果绝对可靠
!./.venv/bin/pip list | grep vllm
```

# 4. (终极版) 使用 .venv 中的 Python 解释器启动服务
```
# 这是最明确、最不会出错的启动方式
!nohup ./.venv/bin/python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2-0.5B-Instruct \
    --trust-remote-code \
    --port 8000 > vllm.log 2>&1 &

# 等待20秒让服务器有足够时间启动，然后查看日志
!sleep 20 && tail -n 20 vllm.log
```

# 5. (最终认证版) 使用 Authtoken 创建公网 URL
```
# 先在Colab的全局环境中安装 pyngrok
!pip install -q pyngrok

from google.colab import userdata
from pyngrok import ngrok

# 注册ngrok账号并获取Authtoken，填入Colab环境变量中
# 从 Colab Secrets 中获取我们存储的 Authtoken
NGROK_TOKEN = userdata.get('NGROK_AUTHTOKEN')

# 设置 ngrok 的认证 token
ngrok.set_auth_token(NGROK_TOKEN)

# 断开所有可能的旧隧道，确保干净的环境
ngrok.kill()

# 连接到 8000 端口，创建新的隧道
public_url = ngrok.connect(8000)

print("✅ 服务隧道创建成功！")
print(f"你的公网URL是: {public_url}")
print("---")
print("请复制上面这个 https://开头的地址，填入你本地电脑的 .env 文件中！")
print("提醒：记得在URL末尾加上 /v1")
```

# 使用 asyncio.Semaphore 进行专业级并发控制
```
import asyncio
import aiohttp
import json
import time
from collections import Counter

# --- 配置参数 ---
URL = "http://localhost:8000/v1/chat/completions"
PAYLOAD_FILE = "tests/payload.json"
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

    headers = {'Content-Type': 'application/json'}
    
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