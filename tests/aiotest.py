import asyncio
import aiohttp
import json
import time
from collections import Counter
import os
from dotenv import load_dotenv
from pathlib import Path
# 在脚本开头加载环境变量
load_dotenv()
API_KEY = os.getenv("API_KEY")

# --- 配置参数 ---
URL = "http://localhost:8000/v1/chat/completions"
SCRIPT_DIR = Path(__file__).parent
PAYLOAD_FILE = SCRIPT_DIR / "payload.json"
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