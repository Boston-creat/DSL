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
from src.logger import setup_logger

# 初始化日志记录器
logger = setup_logger("DSL_Agent_CLI")


def load_script(file_path: str) -> str:
    """加载DSL脚本文件"""
    try:
        logger.info(f"开始加载DSL脚本文件: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"成功加载脚本文件，文件大小: {len(content)} 字符")
        return content
    except FileNotFoundError:
        logger.error(f"文件不存在: {file_path}")
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"无法读取文件 {file_path}: {e}", exc_info=True)
        print(f"错误: 无法读取文件: {e}")
        sys.exit(1)


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("DSL智能客服系统启动")
    logger.info("=" * 60)
    
    if len(sys.argv) < 2:
        logger.warning("命令行参数不足，显示使用说明")
        print("用法: python src/cli.py <script_file> [--llm-client <type>]")
        print("示例: python src/cli.py scripts/order_query.dsl")
        print("示例: python src/cli.py scripts/order_query.dsl --llm-client zhipuai")
        print("支持的LLM类型: zhipuai(智谱AI)")
        print("\n注意: 本项目要求使用API进行意图识别，必须配置 ZHIPUAI_API_KEY")
        print("配置方法: 创建 .env 文件，添加 ZHIPUAI_API_KEY=your_key")
        sys.exit(1)
    
    script_file = sys.argv[1]
    logger.info(f"脚本文件路径: {script_file}")
    
    # 解析命令行参数
    # 默认使用智谱AI（中国可用）
    llm_client_type = "zhipuai"  # 默认使用智谱AI（中国可用）
    if "--llm-client" in sys.argv:
        idx = sys.argv.index("--llm-client")
        if idx + 1 < len(sys.argv):
            llm_client_type = sys.argv[idx + 1]
            logger.info(f"指定LLM客户端类型: {llm_client_type}")
            if llm_client_type == "simple":
                logger.error("不支持simple模式，要求使用API")
                print("[ERROR] 本项目要求使用API进行意图识别，不支持 simple 模式")
                print("请配置 ZHIPUAI_API_KEY 环境变量")
                sys.exit(1)
    
    # 检查API密钥配置
    if not os.getenv("ZHIPUAI_API_KEY"):
        logger.error("未检测到ZHIPUAI_API_KEY环境变量")
        print("[ERROR] 未检测到智谱AI API密钥")
        print("[*] 本项目要求使用API进行意图识别，必须配置 ZHIPUAI_API_KEY")
        print("[*] 配置方法:")
        print("    1. 创建 .env 文件（在项目根目录）")
        print("    2. 添加: ZHIPUAI_API_KEY=your_key")
        print("    3. 获取API密钥: 访问 https://open.bigmodel.cn/")
        sys.exit(1)
    else:
        logger.info("API密钥配置检查通过")
    
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
    logger.info("开始词法分析")
    lexer = Lexer(script_content)
    try:
        tokens = lexer.tokenize()
        logger.info(f"词法分析完成，共生成 {len(tokens)} 个Token")
        print(f"[OK] 词法分析完成，共 {len(tokens)} 个Token")
    except SyntaxError as e:
        logger.error(f"词法分析错误: {e}", exc_info=True)
        print(f"[ERROR] 词法分析错误: {e}")
        sys.exit(1)
    
    # 语法分析
    print("[*] 语法分析中...")
    logger.info("开始语法分析")
    # 重新创建lexer，因为之前的lexer已经被消耗了
    lexer = Lexer(script_content)
    parser = Parser(lexer)
    try:
        program = parser.parse()
        logger.info(f"语法分析完成，共解析出 {len(program.intents)} 个意图")
        print(f"[OK] 语法分析完成，共 {len(program.intents)} 个意图")
    except SyntaxError as e:
        logger.error(f"语法分析错误: {e}", exc_info=True)
        print(f"[ERROR] 语法分析错误: {e}")
        sys.exit(1)
    
    # 创建LLM客户端
    print("[*] 初始化LLM客户端...")
    logger.info(f"初始化LLM客户端，类型: {llm_client_type}")
    try:
        llm_client = create_llm_client(llm_client_type)
        logger.info("LLM客户端初始化成功")
        print(f"[OK] LLM客户端初始化完成")
    except (ValueError, ImportError, RuntimeError) as e:
        logger.error(f"LLM客户端初始化失败: {e}", exc_info=True)
        print(f"[ERROR] LLM客户端初始化失败: {e}")
        sys.exit(1)
    
    # 创建解释器
    logger.info("创建解释器实例")
    interpreter = Interpreter(llm_client)
    # 通过interpret方法初始化，确保intents正确设置
    interpreter.interpret(program)
    
    # 设置用户输入回调
    def get_user_input(prompt: str) -> str:
        logger.debug(f"等待用户输入: {prompt}")
        return input(f"请输入 {prompt}: ")
    
    interpreter.set_user_input_callback(get_user_input)
    
    print("-" * 50)
    print("[*] 系统就绪，请输入您的问题（输入 'quit' 退出）")
    print("-" * 50)
    logger.info("系统初始化完成，进入交互模式")
    
    # 交互循环
    while True:
        try:
            user_input = input("\n您: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                logger.info("用户退出系统")
                print("[*] 再见！")
                break
            
            if not user_input:
                continue
            
            logger.info(f"收到用户输入: {user_input}")
            
            # 意图识别
            print("[*] 识别意图中...")
            logger.debug("开始意图识别")
            matched_intent = interpreter.match_intent(user_input)
            
            if not matched_intent:
                logger.warning(f"未能识别用户意图，输入: {user_input}")
                print("[!] 抱歉，我没有理解您的意图。请尝试其他表达方式。")
                print(f"[DEBUG] 用户输入: '{user_input}'")
                if hasattr(interpreter, 'intents') and interpreter.intents:
                    print(f"[DEBUG] 可用意图数量: {len(interpreter.intents)}")
                    for intent in interpreter.intents:
                        if hasattr(intent, 'when_clause') and hasattr(intent.when_clause, 'patterns'):
                            print(f"[DEBUG] 意图 '{intent.name}' 的模式: {intent.when_clause.patterns}")
                continue
            
            logger.info(f"识别到意图: {matched_intent.name}")
            print(f"[OK] 识别到意图: {matched_intent.name}")
            
            # 执行意图
            logger.debug(f"开始执行意图: {matched_intent.name}")
            result = interpreter.execute_intent(matched_intent)
            logger.debug(f"意图执行完成: {matched_intent.name}")
            
        except KeyboardInterrupt:
            logger.info("用户中断程序（KeyboardInterrupt）")
            print("\n[*] 再见！")
            break
        except Exception as e:
            logger.error(f"发生未预期的错误: {e}", exc_info=True)
            print(f"[ERROR] 发生错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

