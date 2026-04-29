# RWKV批量测试

RWKV 模型批量测试与评估工具 - 通过锦标赛机制测试模型性能。

## 项目概述

本项目通过三层流程来评估 LLM 模型：
1. **问题生成** - 使用线上 API (DeepSeek) 生成各类测试问题
2. **答案生成** - 使用本地 API 批量生成多个答案
3. **锦标赛打分** - 使用线上 API 进行多轮次淘汰赛制打分

## 项目结构

```
RWKV批量测试/
├── config.py              # 配置文件（API密钥、路径、参数）
├── api_clients.py         # API 客户端封装（线上+本地）
├── prompts.py             # 提示词模板库
├── utils.py               # 工具函数（JSON读写、提取器）
├── main.py                # 命令行入口
├── app.py                 # Streamlit Web UI 入口
├── modules/
│   ├── __init__.py
│   ├── question_gen.py    # 问题生成模块
│   ├── answer_gen.py      # 答案生成模块
│   └── tournament_eval.py # 锦标赛评估模块
└── data/
    ├── questions/         # 生成的问题存储
    ├── raw_answers/       # 原始答案存储
    ├── tournament/        # 锦标赛结果存储
    └── logs/              # 日志文件
```

## 功能特性

### 1. 问题生成
- 支持预设主题：数学、代码、逻辑、物理、阅读理解、创意写作、翻译
- 支持中文和英文双语
- 支持自定义提示词
- 支持批量生成

### 2. 答案生成
- 本地 API 批量并发生成
- 支持 `N_VALUE` 参数控制样本数量：`8 * (2^N)`
- 可配置生成参数（temperature, top_k, top_p 等）
- 自动跳过已生成的问题

### 3. 锦标赛评估
- 多轮次淘汰赛制
- 每轮 8 个答案分组打分
- 自动提取排名并保留优胜者
- 支持指定打分层级

## 配置说明

编辑 [config.py](file:///c:\Work\Test-AI-by-AI\Test-AI-By-LLM\config.py) 配置 API 和参数：

```python
# 线上 API 配置
DEEPSEEK_API_KEY = "your-api-key"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"

# 本地 API 配置
LOCAL_API_URL = "http://192.168.0.125:8001/v1/chat/completions"
LOCAL_API_PWD = "rwkv7_7.2b"

# 实验参数
N_VALUE = 2  # 样本数量 = 8 * (2^N)
```

## 使用方法

### 方式一：命令行

```bash
python main.py
```

菜单选项：
1. 生成测试问题
2. 批量生成回复
3. 执行层级打分与淘汰
0. 退出程序

### 方式二：Streamlit Web UI

```bash
streamlit run app.py
```

访问 http://localhost:8501 使用图形界面。

## 依赖要求

- Python 3.12+
- openai
- requests
- streamlit

安装依赖：
```bash
pip install openai requests streamlit
```

## 数据流程

```
问题生成 (线上API) 
    ↓
data/questions/*.json
    ↓
答案生成 (本地API)
    ↓
data/raw_answers/*.json
    ↓
锦标赛打分 (线上API)
    ↓
data/tournament/{level}/*.json
```

## 核心模块说明

### [api_clients.py](file:///c:\Work\Test-AI-by-AI\Test-AI-By-LLM\api_clients.py)
- `call_online_api()` - 调用 DeepSeek API
- `call_local_api_batch()` - 批量调用本地模型 API

### [modules/question_gen.py](file:///c:\Work\Test-AI-by-AI\Test-AI-By-LLM\modules\question_gen.py)
- `generate_questions()` - 生成测试问题

### [modules/answer_gen.py](file:///c:\Work\Test-AI-by-AI\Test-AI-By-LLM\modules\answer_gen.py)
- `generate_answers_for_all_questions()` - 批量生成答案

### [modules/tournament_eval.py](file:///c:\Work\Test-AI-by-AI\Test-AI-By-LLM\modules\tournament_eval.py)
- `run_tournament()` - 执行锦标赛打分
