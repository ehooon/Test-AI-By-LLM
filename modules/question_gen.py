import uuid
import os
import math
from config import *
from prompts import PRESET_TOPICS, Q_GEN_FORMAT_PREFIX
from api_clients import call_online_api
from utils import save_json, extract_questions_array

def generate_questions(topic_or_prompt, is_preset=True, target_size_b=20, total_questions=1, k_per_call=1, language="中文", log_func=print, stream_func=None):
    questions_saved = 0
    format_prefix = Q_GEN_FORMAT_PREFIX.get(language, Q_GEN_FORMAT_PREFIX["中文"])
    
    if is_preset:
        api_calls_needed = math.ceil(total_questions / k_per_call)
        for i in range(api_calls_needed):
            current_k = min(k_per_call, total_questions - (i * k_per_call))
            base_prompt = PRESET_TOPICS[language][topic_or_prompt].format(size=target_size_b, k=current_k)
            final_prompt = format_prefix + base_prompt
            
            # 【核心修复】：彻底剥离 system 角色，解除对思考模型的智商压制
            messages = [
                {"role": "user", "content": final_prompt}
            ]
            
            log_func(f"⏳ [批次 {i+1}/{api_calls_needed}] 正在等待线上 API 返回结果...")
            log_func(f"📜 **底层提示词:**\n```text\n{final_prompt}\n```")
            
            response_text = call_online_api(messages)
            
            if stream_func and response_text:
                stream_func(response_text)
                
            questions_list = extract_questions_array(response_text)
            if not questions_list:
                log_func(f"⚠️ [批次 {i+1}] 提取失败，跳过本批次。")
                continue
                
            for q_text in questions_list:
                q_id = str(uuid.uuid4())[:8]
                save_path = os.path.join(QUESTIONS_DIR, f"q_{q_id}.json")
                save_json({"id": q_id, "question": q_text, "language": language}, save_path)
                questions_saved += 1
                
            log_func(f"✅ [批次 {i+1}] 成功提取并保存 {len(questions_list)} 个文件。")
            
    else:
        final_prompt = format_prefix + topic_or_prompt
        
        # 【核心修复】：彻底剥离 system 角色
        messages = [
            {"role": "user", "content": final_prompt}
        ]
        
        log_func(f"⏳ 正在等待自定义提示词的 API 返回结果...")
        log_func(f"📜 **底层提示词:**\n```text\n{final_prompt}\n```")
        
        response_text = call_online_api(messages)
        
        if stream_func and response_text:
            stream_func(response_text)
            
        questions_list = extract_questions_array(response_text)
        
        if not questions_list:
            log_func(f"⚠️ 提取问题数组失败。")
        else:
            for q_text in questions_list:
                q_id = str(uuid.uuid4())[:8]
                save_path = os.path.join(QUESTIONS_DIR, f"q_{q_id}.json")
                save_json({"id": q_id, "question": q_text, "language": language}, save_path)
                questions_saved += 1
            log_func(f"✅ 成功从该提示词结果中切分并保存了 {len(questions_list)} 个问题。")
            
    log_func(f"🎉 当前任务结束，共计保存 **{questions_saved}** 个文件。")