import os
import json
import glob

# 数据路径配置
DATA_DIR = "data"
RAW_ANSWERS_DIR = os.path.join(DATA_DIR, "raw_answers")
TOURNAMENT_DIR = os.path.join(DATA_DIR, "tournament")
OUTPUT_DIR = os.path.join(DATA_DIR, "compiled_dataset")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "compiled_groups.jsonl")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("⏳ 正在加载原始长文本答案库...")
    # 建立速查字典: { q_id: { ans_id: content, question: text } }
    raw_contents = {}
    if not os.path.exists(RAW_ANSWERS_DIR):
        print("⚠️ 找不到原始答案文件夹！")
        return
        
    for filename in os.listdir(RAW_ANSWERS_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(RAW_ANSWERS_DIR, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                q_id = data['q_id']
                if q_id not in raw_contents:
                    raw_contents[q_id] = {"question": data['question'], "answers": {}}
                for ans in data['answers']:
                    raw_contents[q_id]["answers"][ans['ans_id']] = ans['content']

    print("⏳ 正在拼接打分结果并生成 JSONL 数据集...")
    compiled_count = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
        # 遍历所有题目的锦标赛文件夹
        for q_dir in glob.glob(os.path.join(TOURNAMENT_DIR, "question_*")):
            q_id = os.path.basename(q_dir).replace("question_", "")
            if q_id not in raw_contents:
                continue
            
            question_text = raw_contents[q_id]["question"]
            content_dict = raw_contents[q_id]["answers"]

            # 遍历层级
            for level_dir in glob.glob(os.path.join(q_dir, "level_*")):
                level = int(os.path.basename(level_dir).replace("level_", ""))
                
                # 遍历组别
                for group_file in glob.glob(os.path.join(level_dir, "group_*.json")):
                    with open(group_file, 'r', encoding='utf-8') as f:
                        g_data = json.load(f)
                    
                    group_idx = g_data['group_idx']
                    scores_result = g_data['scores_result']
                    survivors = set(g_data['survivors'])
                    
                    # 组装本组的完整数据
                    assembled_answers = []
                    for s in scores_result:
                        a_id = s['ans_id']
                        assembled_answers.append({
                            "ans_id": a_id,
                            "score": s['score'],
                            "is_survivor": a_id in survivors,
                            "content": content_dict.get(a_id, "⚠️ 提取内容失败")
                        })
                    
                    # 最终拼接的 JSON 结构
                    line_data = {
                        "q_id": q_id,
                        "level": level,
                        "group_idx": group_idx,
                        "question": question_text,
                        "answers": assembled_answers
                    }
                    
                    # 写入 JSONL
                    out_f.write(json.dumps(line_data, ensure_ascii=False) + "\n")
                    compiled_count += 1

    print(f"✅ 数据拼接大功告成！共整理了 {compiled_count} 个对决组。")
    print(f"📁 结果已保存至: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()