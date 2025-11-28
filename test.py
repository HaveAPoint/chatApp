# 需要先安装openai库：pip install openai
from openai import OpenAI

# 配置您的客户端
client = OpenAI(
    api_key="sk-lcDI4jWQD4jswlJ8DUsjGi3KPviNJsR8Efdz45IUhyWYNecA",  # 请替换为您的真实API密钥
    base_url="https://api.gemai.cc/v1"  # 您提供的API端点
)

# 尝试发起一个简单的聊天完成请求
try:
    response = client.chat.completions.create(
        model="gemini-3-pro-preview",  # 注意：这里需要替换为该服务支持的具体模型名
        messages=[
            {"role": "user", "content": "哈吉米哦南北绿豆"}
        ]
    )
    # 如果请求成功，打印返回内容
    print(response.choices[0].message.content)
except Exception as e:
    print(f"请求出错: {e}")