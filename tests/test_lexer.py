"""
词法分析器测试
"""

import pytest
from src.lexer import Lexer, TokenType


def test_basic_tokens():
    """测试基本Token识别"""
    lexer = Lexer('intent "test" { }')
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.INTENT
    assert tokens[1].type == TokenType.STRING
    assert tokens[1].value == "test"
    assert tokens[2].type == TokenType.LBRACE
    assert tokens[3].type == TokenType.RBRACE


def test_string_literal():
    """测试字符串字面量"""
    lexer = Lexer('"hello world"')
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "hello world"


def test_keywords():
    """测试关键字识别"""
    lexer = Lexer('intent when user_says ask wait_for response set or options')
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.INTENT
    assert tokens[1].type == TokenType.WHEN
    assert tokens[2].type == TokenType.USER_SAYS
    assert tokens[3].type == TokenType.ASK
    assert tokens[4].type == TokenType.WAIT_FOR
    assert tokens[5].type == TokenType.RESPONSE
    assert tokens[6].type == TokenType.SET
    assert tokens[7].type == TokenType.OR
    assert tokens[8].type == TokenType.OPTIONS


def test_identifier():
    """测试标识符"""
    lexer = Lexer('order_number refund_id _test123')
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "order_number"
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[2].type == TokenType.IDENTIFIER


def test_special_characters():
    """测试特殊字符"""
    lexer = Lexer('{ } ( ) [ ] = , $')
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.LBRACE
    assert tokens[1].type == TokenType.RBRACE
    assert tokens[2].type == TokenType.LPAREN
    assert tokens[3].type == TokenType.RPAREN
    assert tokens[4].type == TokenType.LBRACKET
    assert tokens[5].type == TokenType.RBRACKET
    assert tokens[6].type == TokenType.EQUALS
    assert tokens[7].type == TokenType.COMMA
    assert tokens[8].type == TokenType.DOLLAR


def test_comments():
    """测试注释"""
    lexer = Lexer('# This is a comment\nintent "test"')
    tokens = lexer.tokenize()
    
    # 注释应该被跳过
    assert tokens[0].type == TokenType.INTENT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

