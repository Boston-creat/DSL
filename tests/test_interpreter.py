"""
解释器测试
"""

import pytest
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.llm_client import SimpleLLMClient


def test_interpreter_basic():
    """测试解释器基本功能"""
    script = '''
    intent "测试" {
        when user_says "测试" {
            response "测试响应"
        }
    }
    '''
    
    lexer = Lexer(script)
    parser = Parser(lexer)
    program = parser.parse()
    
    llm_client = SimpleLLMClient()
    interpreter = Interpreter(llm_client)
    interpreter.intents = program.intents
    
    # 匹配意图
    matched_intent = interpreter.match_intent("测试")
    assert matched_intent is not None
    assert matched_intent.name == "测试"
    
    # 执行意图
    result = interpreter.execute_intent(matched_intent)
    assert result is not None
    assert "response" in result


def test_interpreter_variables():
    """测试解释器变量管理"""
    script = '''
    intent "测试" {
        when user_says "测试" {
            set test_var = "test_value"
            response "变量值：{test_var}"
        }
    }
    '''
    
    lexer = Lexer(script)
    parser = Parser(lexer)
    program = parser.parse()
    
    llm_client = SimpleLLMClient()
    interpreter = Interpreter(llm_client)
    
    intent = program.intents[0]
    result = interpreter.execute_intent(intent)
    
    assert "test_var" in interpreter.variables
    assert interpreter.variables["test_var"] == "test_value"


def test_interpreter_template_formatting():
    """测试模板字符串格式化"""
    script = '''
    intent "测试" {
        when user_says "测试" {
            set name = "张三"
            response "您好，{name}"
        }
    }
    '''
    
    lexer = Lexer(script)
    parser = Parser(lexer)
    program = parser.parse()
    
    llm_client = SimpleLLMClient()
    interpreter = Interpreter(llm_client)
    
    intent = program.intents[0]
    result = interpreter.execute_intent(intent)
    
    assert "您好，张三" in result["response"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

