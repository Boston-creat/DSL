"""
集成测试 - 测试整个系统的端到端功能
"""

import pytest
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from tests.stubs.mock_llm_client import MockLLMClient


def test_end_to_end_order_query():
    """测试订单查询的端到端流程"""
    script = '''
    intent "订单查询" {
        when user_says "查询订单" or "我的订单" {
            ask "请输入您的订单号"
            wait_for order_number
            response "您的订单 {order_number} 状态是：已发货"
        }
    }
    '''
    
    # 词法分析
    lexer = Lexer(script)
    tokens = lexer.tokenize()
    assert len(tokens) > 0
    
    # 语法分析（需要重新创建lexer，因为tokenize已经消耗了）
    lexer2 = Lexer(script)
    parser = Parser(lexer2)
    program = parser.parse()
    assert len(program.intents) == 1
    
    # 解释执行
    llm_client = MockLLMClient()
    interpreter = Interpreter(llm_client)
    interpreter.intents = program.intents  # 设置意图列表
    
    # 模拟用户输入
    user_inputs = {"order_number": "12345"}
    interpreter.set_user_input_callback(lambda var: user_inputs.get(var, ""))
    
    # 匹配意图
    matched_intent = interpreter.match_intent("查询订单")
    assert matched_intent is not None
    assert matched_intent.name == "订单查询"
    
    # 执行意图
    result = interpreter.execute_intent(matched_intent)
    assert result is not None
    assert "response" in result or result.get("variables", {}).get("order_number") == "12345"


def test_multiple_intents():
    """测试多个意图的场景"""
    script = '''
    intent "订单查询" {
        when user_says "查询订单" {
            response "订单查询"
        }
    }
    
    intent "退款申请" {
        when user_says "退款" {
            response "退款申请"
        }
    }
    '''
    
    lexer = Lexer(script)
    parser = Parser(lexer)
    program = parser.parse()
    
    assert len(program.intents) == 2
    
    llm_client = MockLLMClient()
    interpreter = Interpreter(llm_client)
    interpreter.intents = program.intents
    
    # 测试意图匹配
    intent1 = interpreter.match_intent("查询订单")
    assert intent1.name == "订单查询"
    
    intent2 = interpreter.match_intent("退款")
    assert intent2.name == "退款申请"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

