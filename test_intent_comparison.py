#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
意图识别测试（仅使用智谱AI）

注意：本项目要求使用API进行意图识别，已移除简单匹配功能。
此文件仅用于测试智谱AI的意图识别效果。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.llm_client import create_llm_client

# 加载测试脚本
script_content = """
intent "订单查询" {
    when user_says "查询订单" or "我的订单" or "订单状态" or "查看订单" or "订单查询" or "查订单" or "订单" {
        response "订单查询功能"
    }
}

intent "退款申请" {
    when user_says "退款" or "退货" or "申请退款" or "我要退款" {
        response "退款申请功能"
    }
}

intent "技术支持" {
    when user_says "故障" or "问题" or "无法使用" or "技术支持" {
        response "技术支持功能"
    }
}
"""

# 解析脚本
lexer = Lexer(script_content)
parser = Parser(lexer)
program = parser.parse()

# 测试用例
test_cases = [
    # 完全匹配的情况
    ("查询订单", "订单查询"),
    ("退款", "退款申请"),
    ("故障", "技术支持"),
    
    # 部分匹配的情况
    ("我想查一下订单", "订单查询"),
    ("我的订单在哪里", "订单查询"),
    ("订单号是多少", "订单查询"),
    
    # 同义词/近义词
    ("我想退货", "退款申请"),
    ("申请退款", "退款申请"),
    ("我要退款", "退款申请"),
    
    # 自然语言表达
    ("系统出问题了", "技术支持"),
    ("用不了", "技术支持"),
    ("帮我看看", None),  # 模糊表达，可能无法匹配
    
    # 完全不同的表达
    ("你好", None),
    ("谢谢", None),
]

print("=" * 80)
print("意图识别测试：智谱AI")
print("=" * 80)
print()
print("注意：本项目要求使用API进行意图识别，已移除简单匹配功能。")
print()

# 创建解释器
try:
    llm_client = create_llm_client("zhipuai")
except Exception as e:
    print(f"[ERROR] 无法创建LLM客户端: {e}")
    print("请确保已配置 ZHIPUAI_API_KEY 环境变量")
    sys.exit(1)

interpreter = Interpreter(llm_client)
interpreter.interpret(program)

print(f"测试用例数量: {len(test_cases)}")
print(f"可用意图: {[intent.name for intent in program.intents]}")
print()
print("-" * 80)

# 统计结果
llm_correct = 0
llm_matched = 0

for i, (user_input, expected) in enumerate(test_cases, 1):
    print(f"\n测试 {i}: \"{user_input}\"")
    print(f"期望意图: {expected if expected else '无匹配'}")
    
    # 智谱AI识别
    try:
        llm_intent = interpreter.match_intent(user_input)
        llm_result = llm_intent.name if llm_intent else None
        print(f"智谱AI:   {llm_result if llm_result else '无匹配'}", end="")
        if llm_result:
            llm_matched += 1
            if llm_result == expected:
                print(" [正确]")
                llm_correct += 1
            else:
                print(f" [错误，期望: {expected}]")
        else:
            if expected is None:
                print(" [正确]")
                llm_correct += 1
            else:
                print(f" [错误，期望: {expected}]")
    except Exception as e:
        print(f" [错误: {e}]")

print()
print("=" * 80)
print("统计结果")
print("=" * 80)
print(f"总测试数: {len(test_cases)}")
print()
print("智谱AI:")
print(f"  匹配成功: {llm_matched}/{len(test_cases)} ({llm_matched*100//len(test_cases) if test_cases else 0}%)")
print(f"  识别正确: {llm_correct}/{len(test_cases)} ({llm_correct*100//len(test_cases) if test_cases else 0}%)")
print()
print("=" * 80)
print("说明:")
print("=" * 80)
print("1. 智谱AI的优势:")
print("   - 能理解自然语言表达和同义词")
print("   - 能处理模糊、不完整的输入")
print("   - 能理解上下文和语义")
print("   - 对'我想查一下订单'、'系统出问题了'等表达识别更好")
print()
print("2. 本项目要求:")
print("   - 使用API进行意图识别")
print("   - 必须配置 ZHIPUAI_API_KEY 环境变量")
print("   - 不支持简单匹配模式")
print("=" * 80)
