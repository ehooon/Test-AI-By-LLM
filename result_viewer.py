import streamlit as st
import json
import os

st.set_page_config(page_title="打分数据抽查平台", layout="wide", page_icon="🔍")

DATA_FILE = "data/compiled_dataset/compiled_groups.jsonl"

@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    data = []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def main():
    st.title("🔍 模型锦标赛打分 - 抽查与对比系统")
    
    data = load_data()
    if not data:
        st.warning(f"⚠️ 找不到数据文件 {DATA_FILE}！请先在终端运行 `python build_dataset.py`。")
        return
        
    # 提取多级菜单数据
    q_ids = sorted(list(set([d['q_id'] for d in data])))
    
    st.sidebar.header("🎯 导航筛选")
    selected_qid = st.sidebar.selectbox("1️⃣ 选择题目 ID", q_ids)
    
    q_data = [d for d in data if d['q_id'] == selected_qid]
    levels = sorted(list(set([d['level'] for d in q_data])))
    selected_level = st.sidebar.selectbox("2️⃣ 选择锦标赛层级", levels)
        
    l_data = [d for d in q_data if d['level'] == selected_level]
    groups = sorted(list(set([d['group_idx'] for d in l_data])))
    selected_group = st.sidebar.selectbox("3️⃣ 选择对抗组别", groups)
        
    target_group = next((d for d in l_data if d['group_idx'] == selected_group), None)
    
    if not target_group:
        st.error("无法加载该组数据！")
        return
        
    # 渲染题目区域 (同样使用 text_area 呈现纯文本防解析)
    st.markdown("### ❓ 原始提示词 (输入)")
    st.text_area(
        label="Question", 
        value=target_group['question'], 
        height=100, 
        disabled=True, 
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### ⚔️ 本组打分详情 (8进4)")
    
    # 获取答案并确保按照分数由高到低降序排列
    answers = sorted(target_group['answers'], key=lambda x: x['score'], reverse=True)
    
    # 2排 x 4列 的网格布局渲染
    for row in range(2):
        cols = st.columns(4)
        for col_idx in range(4):
            ans_idx = row * 4 + col_idx
            if ans_idx < len(answers):
                ans = answers[ans_idx]
                with cols[col_idx]:
                    # 动态 UI: 晋级与淘汰的视觉差
                    if ans['is_survivor']:
                        survivor_tag = "✅ **晋级**"
                    else:
                        survivor_tag = "❌ 淘汰"
                        
                    st.markdown(f"#### 🏅 Rank {ans_idx+1} (得分: {ans['score']})")
                    st.caption(f"原生 ID: {ans['ans_id']} | {survivor_tag}")
                    
                    # 核心改动：使用只读的 text_area 组件，实现绝对纯文本与完美换行展示
                    unique_key = f"box_{target_group['q_id']}_{target_group['level']}_{target_group['group_idx']}_{ans['ans_id']}"
                    
                    st.text_area(
                        label="Answer Content",
                        value=ans['content'],
                        height=400,            # 框的固定高度
                        disabled=True,         # 设置为不可编辑
                        label_visibility="collapsed", 
                        key=unique_key
                    )

if __name__ == "__main__":
    main()