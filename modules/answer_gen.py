import os
from config import *
from api_clients import call_local_api_batch
from utils import load_json, save_json, clean_model_output

def generate_answers_for_all_questions(mode="思考模式", n_value=0, max_tokens=1024, temperature=0.8, top_k=50, top_p=0.6, 
                                       alpha_presence=1.0, alpha_frequency=0.1, alpha_decay=0.99, 
                                       log_func=print, stream_func=None):
    samples_per_question = 8 * (2 ** n_value)
    generation_log = load_json(LOG_FILE, {})
    files = [f for f in os.listdir(QUESTIONS_DIR) if f.endswith('.json')]
    
    if not files:
        log_func("⚠️ 找不到问题文件，请先生成问题！")
        return

    for filename in files:
        q_path = os.path.join(QUESTIONS_DIR, filename)
        q_data = load_json(q_path)
        q_id = q_data['id']
        question = q_data['question']
        
        # 将模式加入日志KEY，允许针对同一个问题独立运行不同模式
        log_key = f"{q_id}_{mode}"
        if generation_log.get(log_key):
            log_func(f"⏭️ 跳过已生成的问题: {q_id} ({mode})")
            continue
            
        log_func(f"▶️ 开始为问题 [{q_id}] ({mode}) 并发生成 {samples_per_question} 个回复...")
        
        if mode == "思考模式":
            prompt_suffix = "\n\nAssistant: <think"
            prefix_to_restore = "<think"
        elif mode == "快思考模式":
            prompt_suffix = "\n\nAssistant: <think>\n</think>\n"
            prefix_to_restore = "<think>\n</think>\n"
        else: # 不思考模式
            prompt_suffix = "\n\nAssistant: "
            prefix_to_restore = ""

        # 构造最终 prompts
        contents = [f"User: {question}{prompt_suffix}" for _ in range(samples_per_question)]
        
        def local_stream_handler(results_dict):
            if stream_func and 0 in results_dict:
                stream_func(f"**[并发任务实时预览] 正在监控 Answer 0 ({mode}):**\n\n{prefix_to_restore}{results_dict[0]}")
        
        answers = call_local_api_batch(
            contents, max_tokens=max_tokens, temperature=temperature,
            top_k=top_k, top_p=top_p, alpha_presence=alpha_presence,
            alpha_frequency=alpha_frequency, alpha_decay=alpha_decay,
            stream_callback=local_stream_handler
        )
        
        raw_answers_list = []
        clean_answers_list = []
        
        for i, ans in enumerate(answers):
            # 还原最真实的完整文本
            full_raw_ans = prefix_to_restore + ans
            # 获取去除思维链的纯净内容
            clean_ans = clean_model_output(full_raw_ans)
            
            raw_answers_list.append({"ans_id": i, "content": full_raw_ans})
            clean_answers_list.append({"ans_id": i, "content": clean_ans})
        
        # 保存原生数据
        raw_data = {"q_id": q_id, "question": question, "mode": mode, "answers": raw_answers_list}
        save_path_raw = os.path.join(RAW_ANSWERS_DIR, f"raw_{mode}_{q_id}.json")
        save_json(raw_data, save_path_raw)

        # 保存纯净数据
        clean_data = {"q_id": q_id, "question": question, "mode": mode, "answers": clean_answers_list}
        save_path_clean = os.path.join(CLEAN_ANSWERS_DIR, f"clean_{mode}_{q_id}.json")
        save_json(clean_data, save_path_clean)
        
        generation_log[log_key] = True
        save_json(generation_log, LOG_FILE)
        log_func(f"✅ 问题 [{q_id}] ({mode}) 的 {samples_per_question} 个回复双路生成完毕。")