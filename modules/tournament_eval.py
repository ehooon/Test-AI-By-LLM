import os
import random
from config import *
from prompts import SCORING_PROMPTS
from api_clients import call_online_api
from utils import load_json, save_json, extract_scores_array

def run_tournament(target_levels=1, log_func=print, stream_func=None):
    files = [f for f in os.listdir(RAW_ANSWERS_DIR) if f.endswith('.json')]
    if not files:
        log_func("⚠️ 没有找到任何待打分的原始回答数据！")
        return

    for filename in files:
        data = load_json(os.path.join(RAW_ANSWERS_DIR, filename))
        q_id = data['q_id']
        question = data['question']
        
        # 智能语言溯源：根据题目 ID 去原始题目文件中查询生成的语言（默认回退为中文）
        original_q_data = load_json(os.path.join(QUESTIONS_DIR, f"q_{q_id}.json"), {})
        lang = original_q_data.get("language", "中文")
        scoring_prompt_template = SCORING_PROMPTS.get(lang, SCORING_PROMPTS["中文"])
        
        # 将长文本隔离存放，池子中仅保留 ans_id 进行流转
        content_dict = {ans['ans_id']: ans['content'] for ans in data['answers']}
        current_pool = [{"ans_id": ans['ans_id']} for ans in data['answers']]
        
        log_func(f"\n🏆 **开始锦标赛打分 - 问题 ID: {q_id} (采用 {lang} 提示词)**")
        
        # 以外层题目 ID 创建根文件夹
        q_tournament_dir = os.path.join(TOURNAMENT_DIR, f"question_{q_id}")
        os.makedirs(q_tournament_dir, exist_ok=True)
        
        for level in range(target_levels):
            current_pool_size = len(current_pool)
            
            if current_pool_size < 8:
                log_func(f"ℹ️ 当前池子剩余 {current_pool_size} 个，不足 8 个，本题锦标赛自动结束。")
                break
                
            log_func(f"🔄 --- 正在执行第 {level} 层级打分 (当前池中剩余 {current_pool_size} 个答案) ---")
            
            level_dir = os.path.join(q_tournament_dir, f"level_{level}")
            os.makedirs(level_dir, exist_ok=True)
            
            next_pool = []
            
            # 严格按照 8 个一组进行切分
            groups = [current_pool[i:i+8] for i in range(0, current_pool_size, 8)]
            
            for g_idx, group in enumerate(groups):
                if len(group) != 8:
                    next_pool.extend(group)
                    continue
                    
                answers_text = ""
                for item in group:
                    ans_id = item['ans_id']
                    answers_text += f"--- Answer ID {ans_id} ---\n{content_dict[ans_id]}\n\n"
                    
                # 注入双语自适应的提示词
                prompt = scoring_prompt_template.format(question=question, answers_text=answers_text)
                
                messages = [{"role": "user", "content": prompt}]
                
                response_text = call_online_api(messages)
                
                if stream_func and response_text:
                    stream_func(response_text)
                    
                scores_array = extract_scores_array(response_text)
                
                valid_group_ids = {item['ans_id'] for item in group}
                scores_array = [s for s in scores_array if s.get('ans_id') in valid_group_ids]
                
                missing_ids = valid_group_ids - {s.get('ans_id') for s in scores_array}
                for mid in missing_ids:
                    scores_array.append({"ans_id": mid, "score": random.randint(50, 90)})
                    
                scores_array.sort(key=lambda x: int(x.get('score', 0)), reverse=True)
                
                best_item = scores_array[0]
                worst_item = scores_array[7]
                
                middle_candidates = scores_array[1:7]
                random_two = random.sample(middle_candidates, 2)
                
                group_survivors = [best_item, worst_item] + random_two
                for s in group_survivors:
                    next_pool.append({"ans_id": s["ans_id"]})
                
                group_save_path = os.path.join(level_dir, f"group_{g_idx}.json")
                save_json({
                    "q_id": q_id, 
                    "level": level, 
                    "group_idx": g_idx,
                    "language": lang,
                    "scores_result": scores_array,
                    "survivors": [s["ans_id"] for s in group_survivors]
                }, group_save_path)
            
            log_func(f"✅ 层级 {level} 完毕，本层打分结果已存至 `{level_dir}/` 文件夹下。本层共晋级 {len(next_pool)} 个答案。")
            current_pool = next_pool
            
        log_func(f"🎉 问题 {q_id} 的锦标赛任务执行完毕！最终剩余 {len(current_pool)} 个候选答案。")