"""
命令行界面（CLI）
作用：提供用户交互界面，加载DSL脚本，处理用户输入，执行解释器
在全项目中的作用：这是整个系统的入口点，整合了词法分析、语法分析、解释执行和LLM意图识别等所有模块
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.llm_client import create_llm_client


def load_script(file_path: str) -> str:
    """加载DSL脚本文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 无法读取文件: {e}")
        sys.exit(1)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python src/cli.py <script_file> [--llm-client <type>]")
        print("示例: python src/cli.py scripts/order_query.dsl")
        print("示例: python src/cli.py scripts/order_query.dsl --llm-client zhipuai")
        print("支持的LLM类型: zhipuai(智谱AI), simple(简单匹配)")
        sys.exit(1)
    
    script_file = sys.argv[1]
    
    # 解析命令行参数
    # 默认尝试使用智谱AI（中国可用），如果未配置则使用简单匹配
    llm_client_type = "zhipuai"  # 默认使用智谱AI（中国可用）
    if "--llm-client" in sys.argv:
        idx = sys.argv.index("--llm-client")
        if idx + 1 < len(sys.argv):
            llm_client_type = sys.argv[idx + 1]
    elif not os.getenv("ZHIPUAI_API_KEY"):
        # 如果没有配置API密钥，提示使用简单匹配
        print("[*] 提示: 未检测到智谱AI API密钥")
        print("[*] 支持的类型: zhipuai(智谱AI), simple(简单匹配)")
        print("[*] 将尝试使用智谱AI，如果失败将自动降级到简单匹配")
        print("[*] 配置方法: 创建.env文件，添加 ZHIPUAI_API_KEY=your_key")
        print("-" * 50)
    
    # 设置输出编码（Windows兼容）
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print(f"[*] 加载脚本: {script_file}")
    print(f"[*] LLM客户端: {llm_client_type}")
    print("-" * 50)
    
    # 加载脚本
    script_content = load_script(script_file)
    
    # 词法分析
    print("[*] 词法分析中...")
    lexer = Lexer(script_content)
    try:
        tokens = lexer.tokenize()
        print(f"[OK] 词法分析完成，共 {len(tokens)} 个Token")
    except SyntaxError as e:
        print(f"[ERROR] 词法分析错误: {e}")
        sys.exit(1)
    
    # 语法分析
    print("[*] 语法分析中...")
    # 重新创建lexer，因为之前的lexer已经被消耗了
    lexer = Lexer(script_content)
    parser = Parser(lexer)
    try:
        program = parser.parse()
        print(f"[OK] 语法分析完成，共 {len(program.intents)} 个意图")
    except SyntaxError as e:
        print(f"[ERROR] 语法分析错误: {e}")
        sys.exit(1)
    
    # 创建LLM客户端
    print("[*] 初始化LLM客户端...")
    llm_client = create_llm_client(llm_client_type)
    print(f"[OK] LLM客户端初始化完成")
    
    # 创建解释器
    interpreter = Interpreter(llm_client)
    # 通过interpret方法初始化，确保intents正确设置
    interpreter.interpret(program)
    
    # 设置用户输入回调
    def get_user_input(prompt: str) -> str:
        return input(f"请输入 {prompt}: ")
    
    interpreter.set_user_input_callback(get_user_input)
    
    print("-" * 50)
    print("[*] 系统就绪，请输入您的问题（输入 'quit' 退出）")
    print("-" * 50)
    
    # 交互循环
    while True:
        try:
            user_input = input("\n您: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("[*] 再见！")
                break
            
            if not user_input:
                continue
            
            # 意图识别
            print("[*] 识别意图中...")
            matched_intent = interpreter.match_intent(user_input)
            
            if not matched_intent:
                print("[!] 抱歉，我没有理解您的意图。请尝试其他表达方式。")
                print(f"[DEBUG] 用户输入: '{user_input}'")
                if hasattr(interpreter, 'intents') and interpreter.intents:
                    print(f"[DEBUG] 可用意图数量: {len(interpreter.intents)}")
                    for intent in interpreter.intents:
                        if hasattr(intent, 'when_clause') and hasattr(intent.when_clause, 'patterns'):
                            print(f"[DEBUG] 意图 '{intent.name}' 的模式: {intent.when_clause.patterns}")
                continue
            
            print(f"[OK] 识别到意图: {matched_intent.name}")
            
            # 执行意图
            result = interpreter.execute_intent(matched_intent)
            
        except KeyboardInterrupt:
            print("\n[*] 再见！")
            break
        except Exception as e:
            print(f"[ERROR] 发生错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

