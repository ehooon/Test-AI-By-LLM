# LLM 锦标赛评估工具

一个用于大规模语言模型评估的框架，通过锦标赛机制测试和比较模型性能。

## 项目概述

本项目通过三层流程来评估 LLM 模型：
1. **问题生成** - 使用线上 API (DeepSeek) 生成各类测试问题
2. **答案生成** - 使用本地 API 批量生成多个答案
3. **锦标赛打分** - 使用线上 API 进行多轮次淘汰赛制打分

## 项目结构

```
llm_tournament_eval/
├── config.py                 # 全局配置参数 (API Keys, 路径, N值)
├── prompts.py                # 预设的提示词库 (问题生成、打分)
├── main.py                   # 主程序入口，包含可独立执行的功能菜单
├── utils.py                  # 工具类 (文件读写, 日志处理, JSON解析)
├── api_clients.py            # API 交互层 (包含本地模型 SSE 解析, 线上模型调用)
├── modules/
│   ├── __init__.py
│   ├── question_gen.py       # 功能1：问题生成模块
│   ├── answer_gen.py         # 功能2：本地模型批量答案生成模块
│   └── tournament_eval.py    # 功能3：层级打分与淘汰模块
└── data/                     # 数据存储目录 (程序自动生成)
    ├── questions/            # 生成的测试问题
    ├── raw_answers/          # 本地模型生成的原始答案
    ├── clean_answers/        # 纯净回答存储 (去除思维链)
    ├── tournament/           # N+1 个层级的打分结果文件夹 (0, 1, ..., N)
    └── logs/                 # 生成日志 (避免重复生成)
```

## 功能特性

### 1. 问题生成
- 支持预设主题：数学、代码、逻辑、物理、阅读理解、创意写作、翻译
- 支持中文和英文双语
- 支持自定义提示词
- 批量生成并自动保存为 JSON 文件
- 严格 JSON 格式输出，带格式前置指令

### 2. 答案生成
- 本地 API 批量并发生成
- 支持 `N_VALUE` 参数控制样本数量：`8 * (2^N)`
- 三种生成模式：
  - 思考模式 (`<think`)
  - 不思考模式
  - 快思考模式 (`<think></think>`)
- 可配置生成参数（temperature, top_k, top_p 等）
- 自动去除思维链标签，保存纯净答案
- 自动跳过已生成的问题

### 3. 锦标赛评估
- 多轮次淘汰赛制
- 每轮 8 个答案分组打分
- 自动提取分数并保留优胜者
- 支持指定打分层级
- 0-100 绝对分数评估
- 双语打分提示词

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

### 命令行运行

```bash
python main.py
```

菜单选项：
1. **生成测试问题** (调用线上API)
   - a. 使用内置提示词 (数学/代码/逻辑)
   - b. 手动输入完整提示词
2. **批量生成回复** (调用本地API, 自动跳过已生成)
   - 思考模式
   - 不思考模式
   - 快思考模式
3. **执行层级打分与淘汰** (调用线上API)
0. **退出程序**

## 依赖要求

- Python 3.12+
- openai
- requests

安装依赖：
```bash
pip install openai requests
```

## 数据流程

```
问题生成 (线上API) 
    ↓
data/questions/*.json
    ↓
答案生成 (本地API)
    ↓
data/raw_answers/*.json (原始)
data/clean_answers/*.json (纯净)
    ↓
锦标赛打分 (线上API)
    ↓
data/tournament/{level}/*.json
```

## 核心模块说明

### [api_clients.py](file:///c:\Work\Test-AI-by-AI\Test-AI-By-LLM\api_clients.py)
- `call_online_api()` - 调用 DeepSeek API
- `call_local_api_batch()` - 批量调用本地模型 API (SSE 流式解析)

### [utils.py](file:///c:\Work\Test-AI-by-AI\Test-AI-By-LLM\utils.py)
- `load_json()` / `save_json()` - JSON 文件读写
- `extract_questions_array()` - 提取问题数组
- `extract_scores_array()` - 提取分数数组
- `clean_model_output()` - 去除思维链标签

### [modules/question_gen.py](file:///c:\Work\Test-AI-by-AI\Test-AI-By-LLM\modules\question_gen.py)
- `generate_questions()` - 生成测试问题

### [modules/answer_gen.py](file:///c:\Work\Test-AI-by-AI\Test-AI-By-LLM\modules\answer_gen.py)
- `generate_answers_for_all_questions()` - 批量生成答案

### [modules/tournament_eval.py](file:///c:\Work\Test-AI-by-AI\Test-AI-By-LLM\modules\tournament_eval.py)
- `run_tournament()` - 执行锦标赛打分

## 开发日志

- **20260429** - 完成初版，支持题目生成、批量答案获取、锦标赛打分
