"""
使用测试桩的测试用例
作用：演示如何使用测试桩进行隔离测试
"""

import pytest
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from tests.stubs.mock_llm_client import MockLLMClient, FailingLLMClient


def test_with_mock_llm_client():
    """测试使用Mock LLM客户端"""
    script = '''
    intent "订单查询" {
        when user_says "查询订单" {
            response "订单查询响应"
        }
    }
    '''
    
    lexer = Lexer(script)
    parser = Parser(lexer)
    program = parser.parse()
    
    # 使用Mock客户端
    mock_client = MockLLMClient({
        "查询订单": "订单查询"
    })
    
    interpreter = Interpreter(mock_client)
    interpreter.intents = program.intents
    
    # 测试意图识别
    matched_intent = interpreter.match_intent("查询订单")
    assert matched_intent is not None
    assert matched_intent.name == "订单查询"
    
    # 验证Mock客户端被调用
    assert mock_client.get_call_count() == 1
    assert mock_client.get_last_call()['user_input'] == "查询订单"


def test_with_failing_llm_client():
    """测试LLM客户端失败时的降级处理"""
    script = '''
    intent "订单查询" {
        when user_says "查询订单" {
            response "订单查询响应"
        }
    }
    '''
    
    lexer = Lexer(script)
    parser = Parser(lexer)
    program = parser.parse()
    
    # 使用失败的客户端
    failing_client = FailingLLMClient()
    interpreter = Interpreter(failing_client)
    interpreter.intents = program.intents
    
    # 应该能够降级到简单匹配
    matched_intent = interpreter.match_intent("查询订单")
    # 由于有降级处理，应该仍然能匹配
    assert matched_intent is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

