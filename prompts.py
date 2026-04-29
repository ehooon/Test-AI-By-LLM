PRESET_TOPICS = {
    "中文": {
        "数学": "请生成 {k} 道复杂的数学应用题，用于测试 {size}B 参数的大型语言模型。请仅输出问题内容，不要输出解答。",
        "代码": "请生成 {k} 道复杂的算法编程题，用于测试 {size}B 参数的大型语言模型。请仅输出问题内容。",
        "逻辑": "请生成 {k} 道复杂的逻辑推理题，用于测试 {size}B 参数的大规模语言模型。请仅输出问题内容。",
        "物理": "请生成 {k} 道具有挑战性的物理题，涉及力学或电磁学，用于测试 {size}B 参数的模型。仅输出问题内容。",
        "阅读理解": "请提供 {k} 段约300字的复杂背景文本，并基于每段文本生成一道深度分析题。仅输出文本和问题。",
        "创意写作": "请提供 {k} 个独特的科幻或奇幻世界观设定约束，要求测试模型写一篇微小说。仅输出题目要求。",
        "翻译": "请提供 {k} 段包含长难句和专业术语的中文文本，要求将其翻译为流畅的英文。仅输出待翻译内容及要求。"
    },
    "English": {
        "数学": "Generate {k} complex math word problems suitable for testing a {size}B parameter model. Output only the questions.",
        "代码": "Generate {k} programming algorithm problems suitable for testing a {size}B parameter model. Output only the questions.",
        "逻辑": "Generate {k} complex logical reasoning puzzles suitable for testing a {size}B parameter model. Output only the questions.",
        "物理": "Generate {k} challenging physics problems involving mechanics or electromagnetism. Output only the questions.",
        "阅读理解": "Provide {k} complex background texts of about 300 words and generate a deep analytical question based on each. Output only the texts and questions.",
        "创意写作": "Provide {k} unique sci-fi or fantasy world-building constraints and ask the model to write a flash fiction. Output only the prompts.",
        "翻译": "Provide {k} paragraphs of English text containing complex sentences and jargon, requesting fluent translations into Chinese. Output only the texts and requests."
    }
}

# 【新增】双语前置指令，确保在不影响末尾权重的情况下强制模型输出 JSON
Q_GEN_FORMAT_PREFIX = {
    "中文": "[格式要求]\n你必须严格按照 JSON 对象格式输出，其中必须仅包含一个键 \"questions\"，其值为一个字符串数组，数组内为生成的所有问题。\n示例：\n{\"questions\": [\"问题1的内容...\", \"问题2的内容...\"]}\n除了该 JSON 对象外，请勿输出任何其他内容。\n\n[用户指令]\n",
    "English": "[Format Requirement]\nYou must output strictly as a JSON object with a single key \"questions\". The value must be a JSON array of strings containing the generated questions.\nExample:\n{\"questions\": [\"Question 1...\", \"Question 2...\"]}\nDo not output anything outside this JSON object.\n\n[User Instruction]\n"
}

# =============================================================================
# 提示词模板
# =============================================================================


# 锦标赛打分专用提示词字典 (无角色扮演，纯指令，结构化，支持双语)
SCORING_PROMPTS = {
    "English": """[INSTRUCTION]
Evaluate the following 8 answers based on their accuracy, reasoning, and clarity in response to the provided question. Assign an absolute score from 0 to 100 for each answer.

[FORMAT REQUIREMENT]
Output ONLY a valid JSON object with a single key "scores". The value must be an array of objects, each containing "ans_id" (integer) and "score" (integer).
Example:
{{"scores": [{{"ans_id": 3, "score": 95}}, {{"ans_id": 0, "score": 88}}, {{"ans_id": 7, "score": 82}}, {{"ans_id": 1, "score": 75}}, {{"ans_id": 2, "score": 70}}, {{"ans_id": 5, "score": 60}}, {{"ans_id": 6, "score": 50}}, {{"ans_id": 4, "score": 40}}]}}

[QUESTION]
{question}

[ANSWERS TO EVALUATE]
{answers_text}""",

    "中文": """[指令]
请根据准确性、逻辑推理和清晰度，对以下 8 个针对给定问题的回答进行客观评估。请为每个回答分配一个 0 到 100 的绝对分数。

[格式要求]
必须仅输出一个有效的 JSON 对象，包含唯一键 "scores"。其值必须是一个对象数组，每个对象包含 "ans_id" (整数) 和 "score" (整数)。
示例：
{{"scores": [{{"ans_id": 3, "score": 95}}, {{"ans_id": 0, "score": 88}}, {{"ans_id": 7, "score": 82}}, {{"ans_id": 1, "score": 75}}, {{"ans_id": 2, "score": 70}}, {{"ans_id": 5, "score": 60}}, {{"ans_id": 6, "score": 50}}, {{"ans_id": 4, "score": 40}}]}}

[问题]
{question}

[待评估的回答]
{answers_text}"""
}