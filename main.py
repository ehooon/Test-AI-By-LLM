from modules.question_gen import generate_questions
from modules.answer_gen import generate_answers_for_all_questions
from modules.tournament_eval import run_tournament

def main():
    while True:
        print("\n=== RWKV批量测试 ===")
        print("1. 生成测试问题 (调用线上API)")
        print("2. 批量生成回复 (调用本地API, 自动跳过已生成)")
        print("3. 执行层级打分与淘汰 (调用线上API)")
        print("0. 退出程序")
        
        choice = input("请输入选项 (0-3): ")
        
        if choice == '1':
            print("\n选择提示词模式:")
            print("a. 使用内置提示词 (数学/代码/逻辑)")
            print("b. 手动输入完整提示词")
            sub_choice = input("请输入 (a/b): ")
            
            if sub_choice == 'a':
                topic = input("请输入方向 (数学/代码/逻辑): ")
                size = input("请输入目标测试模型大小 (如 20): ")
                generate_questions(topic, is_preset=True, target_size_b=int(size))
            elif sub_choice == 'b':
                prompt = input("请输入完整提示词: ")
                generate_questions(prompt, is_preset=False)
                
        elif choice == '2':
            print("\n请选择生成模式:")
            print("1. 思考模式 (<think)")
            print("2. 不思考模式 ()")
            print("3. 快思考模式 (<think>\\n</think>)")
            mode_map = {"1": "思考模式", "2": "不思考模式", "3": "快思考模式"}
            m_choice = input("请输入选项 (1/2/3): ")
            target_mode = mode_map.get(m_choice, "思考模式")
            
            generate_answers_for_all_questions(mode=target_mode)
            
        elif choice == '3':
            levels = input("请输入希望执行的打分层级次数 (整数): ")
            run_tournament(target_levels=int(levels))
            
        elif choice == '0':
            print("退出...")
            break
        else:
            print("无效输入！")

if __name__ == "__main__":
    main()