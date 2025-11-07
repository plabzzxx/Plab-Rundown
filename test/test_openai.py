
import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量（override=True 确保覆盖系统环境变量）
load_dotenv(override=True)

print("--- 开始独立 OpenAI API 测试 ---")

# 1. 从环境变量读取 API Key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("错误：未找到 OPENAI_API_KEY 环境变量。")
    exit()

print(f"成功读取到 API Key (前5位): {api_key[:5]}...")
print(f"API Key (后5位): ...{api_key[-5:]}")

# 2. 初始化 OpenAI 客户端
try:
    client = OpenAI(api_key=api_key)
    print("OpenAI 客户端初始化成功。")
except Exception as e:
    print(f"客户端初始化失败: {e}")
    exit()

# 3. 发起一个简单的 API 请求
try:
    print("正在尝试调用 chat.completions.create...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Hello, world!"}
        ]
    )
    print("API 调用成功！")
    print("返回内容:", response.choices[0].message.content)

except Exception as e:
    print(f"!!! API 调用失败: {e}")

print("--- 测试结束 ---")
