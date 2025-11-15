"""
语法分析器测试
"""

import pytest
from src.lexer import Lexer
from src.parser import Parser, IntentDecl, AskAction, ResponseAction, OptionsAction, SetAction


def test_parse_simple_intent():
    """测试解析简单意图"""
    script = '''
    intent "订单查询" {
        when user_says "查询订单" {
            ask "请输入订单号"
            wait_for order_number
            response "订单状态：已发货"
        }
    }
    '''
    
    lexer = Lexer(script)
    parser = Parser(lexer)
    program = parser.parse()
    
    assert len(program.intents) == 1
    assert program.intents[0].name == "订单查询"
    assert len(program.intents[0].actions) == 3


def test_parse_multiple_patterns():
    """测试解析多个匹配模式"""
    script = '''
    intent "退款" {
        when user_says "退款" or "退货" or "申请退款" {
            response "退款处理中"
        }
    }
    '''
    
    lexer = Lexer(script)
    parser = Parser(lexer)
    program = parser.parse()
    
    intent = program.intents[0]
    assert len(intent.when_clause.patterns) == 3
    assert "退款" in intent.when_clause.patterns
    assert "退货" in intent.when_clause.patterns


def test_parse_options():
    """测试解析选项列表"""
    script = '''
    intent "退款" {
        when user_says "退款" {
            options ["质量问题", "不想要了", "其他"]
            wait_for reason
        }
    }
    '''
    
    lexer = Lexer(script)
    parser = Parser(lexer)
    program = parser.parse()
    
    assert len(program.intents) == 1
    # 检查是否有OptionsAction
    options_actions = [a for a in program.intents[0].actions if isinstance(a, OptionsAction)]
    assert len(options_actions) == 1
    assert len(options_actions[0].options) == 3


def test_parse_set_action():
    """测试解析Set动作"""
    script = '''
    intent "测试" {
        when user_says "测试" {
            set refund_id = create_refund("123", "质量问题")
        }
    }
    '''
    
    lexer = Lexer(script)
    parser = Parser(lexer)
    program = parser.parse()
    
    assert len(program.intents) == 1
    set_actions = [a for a in program.intents[0].actions if isinstance(a, SetAction)]
    assert len(set_actions) == 1
    assert set_actions[0].variable == "refund_id"


def test_parse_multiple_intents():
    """测试解析多个意图"""
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
    assert program.intents[0].name == "订单查询"
    assert program.intents[1].name == "退款申请"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

