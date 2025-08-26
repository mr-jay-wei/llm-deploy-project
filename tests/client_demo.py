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
        