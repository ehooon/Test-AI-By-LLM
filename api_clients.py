import json
import requests
from openai import OpenAI
from config import *

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

def call_online_api(messages):
    """【绝对严格】100% 遵循用户提供的 API 调用示例参数，无任何自作主张的删改"""
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,  # 配置中设定为 "deepseek-v4-pro"
            messages=messages,
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}}
        )
        # 严格按照您示例中的取值方式返回
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"线上 API 调用出错: {e}")
        return ""

def call_local_api_batch(contents, max_tokens=1024, temperature=0.8, top_k=50, top_p=0.6, 
                         alpha_presence=1.0, alpha_frequency=0.1, alpha_decay=0.99, stream_callback=None):
    """调用本地模型进行批量生成（完全遵循 curl 示例中的参数结构）"""
    payload = {
        "contents": contents,
        "max_tokens": max_tokens,
        "stop_tokens": [0, 261, 24281],
        "temperature": temperature,
        "top_k": top_k,
        "top_p": top_p,
        "alpha_presence": alpha_presence,
        "alpha_frequency": alpha_frequency,
        "alpha_decay": alpha_decay,
        "stream": True,
        "password": LOCAL_API_PWD
    }
    
    try:
        response = requests.post(LOCAL_API_URL, json=payload, stream=True)
        results = {i: "" for i in range(len(contents))}
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str.strip() == "[DONE]":
                        continue
                    try:
                        data = json.loads(data_str)
                        for choice in data.get("choices", []):
                            idx = choice["index"]
                            content = choice.get("delta", {}).get("content", "")
                            results[idx] += content
                            
                        # 本地 API 保留流式回调 (因为 curl 里是 stream: true)
                        if stream_callback:
                            stream_callback(results)
                    except json.JSONDecodeError:
                        pass
        return [results[i] for i in range(len(contents))]
    except Exception as e:
        print(f"本地 API 调用出错: {e}")
        return [""] * len(contents)