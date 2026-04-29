import json
import os
import re

def load_json(filepath, default_val=None):
    if not os.path.exists(filepath):
        return default_val if default_val is not None else {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_ranking_array(text):
    if not text:
        return None
        
    try:
        data = json.loads(text)
        if "ranking" in data and isinstance(data["ranking"], list):
            return data["ranking"]
    except json.JSONDecodeError:
        pass
        
    match_obj = re.search(r'\{.*?"ranking"\s*:\s*(\[[0-9\s,]+\]).*?\}', text, re.DOTALL)
    if match_obj:
        try:
            return json.loads(match_obj.group(1))
        except:
            pass
            
    match_arr = re.search(r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]', text)
    if match_arr:
        try:
            return json.loads(match_arr.group(0))
        except:
            pass
            
    return None

def extract_questions_array(text):
    if not text:
        return []
        
    try:
        data = json.loads(text)
        if "questions" in data and isinstance(data["questions"], list):
            return data["questions"]
    except json.JSONDecodeError:
        pass
        
    match_obj = re.search(r'\{.*?"questions"\s*:\s*(\[.*?\]).*?\}', text, re.DOTALL)
    if match_obj:
        try:
            return json.loads(match_obj.group(1))
        except:
            pass
            
    match_arr = re.search(r'\[\s*".*?"\s*\]', text, re.DOTALL)
    if match_arr:
        try:
            return json.loads(match_arr.group(0))
        except:
            pass
            
    return []

def clean_model_output(text):
    """
    去除模型输出的思维链标签及其内部所有内容，返回纯净回答。
    """
    if not text:
        return ""
    
    # 非贪婪匹配并去除完整的 <think>...</think> 块，允许跨行
    cleaned = re.sub(r'<think.*?</think>', '', text, flags=re.DOTALL)
    
    # 清理可能遗留的单一残缺标签(比如偶尔没闭合的情况)
    cleaned = re.sub(r'</?think>', '', cleaned)
    
    # 去除首尾的空格和换行符
    return cleaned.strip()

def extract_scores_array(text):
    if not text:
        return []
        
    try:
        data = json.loads(text)
        if "scores" in data and isinstance(data["scores"], list):
            return data["scores"]
    except json.JSONDecodeError:
        pass
        
    # 如果没按纯JSON格式输出，使用正则兜底提取
    match_obj = re.search(r'\{.*?"scores"\s*:\s*(\[\s*\{.*?\}\s*\]).*?\}', text, re.DOTALL)
    if match_obj:
        try:
            return json.loads(match_obj.group(1))
        except:
            pass
            
    return []