import os
from openai import OpenAI

# 从环境变量读取 key，更安全
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("请先设置环境变量 OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "My Demo",
    },
)
response = client.chat.completions.create(
    model="deepseek/deepseek-v4-flash",
    messages=[{"role": "user", "content": "hi"}],
    # 暂时不传任何其他参数
)
print(response)