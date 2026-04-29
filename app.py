import streamlit as st
import time
from modules.question_gen import generate_questions
from modules.answer_gen import generate_answers_for_all_questions
from modules.tournament_eval import run_tournament
from prompts import PRESET_TOPICS

st.set_page_config(page_title="RWKV批量测试", layout="wide")
st.title("🏆 RWKV批量测试 - 数据生成与评估工具")

tab1, tab2, tab3 = st.tabs(["📌 第一步：问题生成", "🤖 第二步：本地模型答案生成", "⚖️ 第三步：API打分与淘汰"])

class StreamRenderer:
    def __init__(self, container):
        self.container = container
        self.last_update = 0
        
    def update(self, text):
        now = time.time()
        if now - self.last_update > 0.1:
            self.container.info(f"**⚡ 实时流响应中...**\n```text\n{text}\n```")
            self.last_update = now
            
    def clear(self):
        self.container.empty()

with tab1:
    st.header("生成测试问题")
    lang_choice = st.radio("选择结构化指令与预设语言", ["中文", "English"], horizontal=True)
    prompt_mode = st.radio("提示词模式", ["使用预设多选", "手动输入多个提示词"], horizontal=True)
    st.divider()
    
    if prompt_mode == "使用预设多选":
        available_topics = list(PRESET_TOPICS[lang_choice].keys())
        selected_topics = st.multiselect("选择生成方向 (可多选)", available_topics, default=["数学", "代码"])
        model_size = st.number_input("目标模型大小 (B)", min_value=1, value=20, step=1)
        manual_prompts = [] 
        
        st.divider()
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            total_q = st.number_input("每个方向独立生成的【总问题数】", min_value=1, value=10, step=1)
        with col_q2:
            k_per_call = st.number_input("单次 API 调用生成的【并发数 K】", min_value=1, value=5, step=1)
    else:
        selected_topics = []
        if "prompt_count" not in st.session_state:
            st.session_state.prompt_count = 1
            
        col_btn1, col_btn2, _ = st.columns([2, 2, 8])
        with col_btn1:
            if st.button("➕ 新增一个提示词窗口"): st.session_state.prompt_count += 1
        with col_btn2:
            if st.button("➖ 移除最后一个窗口") and st.session_state.prompt_count > 1: st.session_state.prompt_count -= 1
                
        st.markdown("---")
        manual_prompts = []
        for i in range(st.session_state.prompt_count):
            p = st.text_area(f"✏️ 提示词窗口 {i+1}:", height=100, key=f"prompt_{i}")
            manual_prompts.append(p)
            
        st.divider()
        total_q, k_per_call = 1, 1 
        st.info("ℹ️ 系统会在您的提示词前拼接结构化 JSON 输出要求，数量由您的提示词自动控制。")
    
    if st.button("🚀 开始生成问题", type="primary"):
        log_container = st.empty()
        stream_container = st.empty()
        renderer = StreamRenderer(stream_container)
        logs = []
        
        def ui_logger(msg):
            logs.append(msg)
            log_container.markdown("\n\n".join(logs))
            
        with st.spinner("任务执行中..."):
            if prompt_mode == "使用预设多选" and selected_topics:
                for topic in selected_topics:
                    ui_logger(f"### 📍 开始生成【{topic}】方向的问题 (共需 {total_q} 个)...")
                    generate_questions(topic, is_preset=True, target_size_b=model_size, total_questions=total_q, 
                                       k_per_call=k_per_call, language=lang_choice, log_func=ui_logger, stream_func=renderer.update)
            elif prompt_mode == "手动输入多个提示词":
                valid_prompts = [p for p in manual_prompts if p.strip()]
                for idx, p in enumerate(valid_prompts):
                    ui_logger(f"### 📍 开始处理【提示词窗口 {idx+1}】...")
                    generate_questions(p, is_preset=False, language=lang_choice, log_func=ui_logger, stream_func=renderer.update)
            renderer.clear()
            st.success("✅ 问题生成任务完毕！")

with tab2:
    st.header("本地模型答案批量生成")
    st.divider()
    
    mode_choice = st.radio("选择模型推理模式", ["思考模式", "不思考模式", "快思考模式"], horizontal=True)
    st.divider()
    
    col_n1, col_n2 = st.columns([1, 2])
    with col_n1:
        n_value = st.number_input("设置本次生成的 N 值 (N >= 0)", min_value=0, value=0, step=1)
    with col_n2:
        st.info(f"💡 当前配置下，将强制为每一个问题生成: **{8 * (2 ** n_value)}** 个结果。")

    st.markdown("### ⚙️ 模型生成参数设置 (Hyperparameters)")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        max_tokens = st.number_input("max_tokens", min_value=1, value=1024, step=128)
        alpha_presence = st.number_input("alpha_presence", value=1.0, step=0.1)
        temperature = st.number_input("temperature", min_value=0.0, value=0.8, step=0.1)
    with col_p2:
        top_k = st.number_input("top_k", min_value=0, value=50, step=5)
        alpha_frequency = st.number_input("alpha_frequency", value=0.1, step=0.05)
    with col_p3:
        top_p = st.number_input("top_p", min_value=0.0, max_value=1.0, value=0.6, step=0.05)
        alpha_decay = st.number_input("alpha_decay", min_value=0.0, max_value=1.0, value=0.99, step=0.01)
        
    st.divider()
    if st.button("⚡ 开始批量生成答案", type="primary"):
        log_container2 = st.empty()
        stream_container2 = st.empty()
        renderer2 = StreamRenderer(stream_container2)
        logs2 = []
        
        def ui_logger2(msg):
            logs2.append(msg)
            log_container2.markdown("\n\n".join(logs2))
            
        with st.spinner("正在调用本地模型 API..."):
            generate_answers_for_all_questions(
                mode=mode_choice,
                n_value=n_value, max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p, 
                alpha_presence=alpha_presence, alpha_frequency=alpha_frequency, alpha_decay=alpha_decay,
                log_func=ui_logger2, stream_func=renderer2.update
            )
        renderer2.clear()
        st.success("批量生成任务完成！已同时保存原生与纯净双份数据！")

with tab3:
    st.header("执行层级锦标赛打分")
    target_levels = st.number_input("期望执行的打分层级数", min_value=1, value=1, step=1)
    
    if st.button("⚖️ 开始打分淘汰", type="primary"):
        log_container3 = st.empty()
        stream_container3 = st.empty()
        renderer3 = StreamRenderer(stream_container3)
        logs3 = []
        
        def ui_logger3(msg):
            logs3.append(msg)
            log_container3.markdown("\n\n".join(logs3))
            
        with st.spinner("正在打分中..."):
            run_tournament(target_levels=target_levels, log_func=ui_logger3, stream_func=renderer3.update)
        renderer3.clear()
        st.success("层级打分全部完成！")