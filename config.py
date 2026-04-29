import os

DEEPSEEK_API_KEY = "sk-da8ef5c3da084837aa168c9cb70c495f"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"

LOCAL_API_URL = "http://192.168.0.125:8001/v1/chat/completions"
LOCAL_API_PWD = "rwkv7_7.2b"

N_VALUE = 2
SAMPLES_PER_QUESTION = 8 * (2 ** N_VALUE)

DATA_DIR = "data"
QUESTIONS_DIR = os.path.join(DATA_DIR, "questions")
RAW_ANSWERS_DIR = os.path.join(DATA_DIR, "raw_answers")
CLEAN_ANSWERS_DIR = os.path.join(DATA_DIR, "clean_answers")  # 新增：纯净回答存储目录
TOURNAMENT_DIR = os.path.join(DATA_DIR, "tournament")
LOG_FILE = os.path.join(DATA_DIR, "logs", "generation_log.json")

for d in [QUESTIONS_DIR, RAW_ANSWERS_DIR, CLEAN_ANSWERS_DIR, TOURNAMENT_DIR, os.path.join(DATA_DIR, "logs")]:
    os.makedirs(d, exist_ok=True)