"""
词法分析器（Lexer）
作用：将DSL脚本源代码分解成一系列Token（词法单元）
在全项目中的作用：这是编译过程的第一步，为语法分析器提供输入
"""

from enum import Enum
from typing import List, Optional


class TokenType(Enum):
    """Token类型枚举"""
    # 关键字
    INTENT = "INTENT"
    WHEN = "WHEN"
    USER_SAYS = "USER_SAYS"
    ASK = "ASK"
    WAIT_FOR = "WAIT_FOR"
    RESPONSE = "RESPONSE"
    SET = "SET"
    OR = "OR"
    OPTIONS = "OPTIONS"
    
    # 字面量
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    
    # 运算符和分隔符
    LBRACE = "LBRACE"      # {
    RBRACE = "RBRACE"      # }
    LPAREN = "LPAREN"      # (
    RPAREN = "RPAREN"      # )
    LBRACKET = "LBRACKET"  # [
    RBRACKET = "RBRACKET"  # ]
    EQUALS = "EQUALS"      # =
    COMMA = "COMMA"        # ,
    DOLLAR = "DOLLAR"      # $
    
    # 特殊
    EOF = "EOF"
    NEWLINE = "NEWLINE"


class Token:
    """Token类，表示一个词法单元"""
    def __init__(self, type: TokenType, value: str, line: int = 0, column: int = 0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line})"


class Lexer:
    """词法分析器"""
    
    KEYWORDS = {
        'intent': TokenType.INTENT,
        'when': TokenType.WHEN,
        'user_says': TokenType.USER_SAYS,
        'ask': TokenType.ASK,
        'wait_for': TokenType.WAIT_FOR,
        'response': TokenType.RESPONSE,
        'set': TokenType.SET,
        'or': TokenType.OR,
        'options': TokenType.OPTIONS,
    }
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
    
    def error(self, message: str):
        """抛出词法分析错误"""
        raise SyntaxError(f"Lexer error at line {self.line}, column {self.column}: {message}")
    
    def advance(self):
        """移动到下一个字符"""
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        
        self.pos += 1
        self.column += 1
        
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def skip_whitespace(self):
        """跳过空白字符"""
        while self.current_char and self.current_char in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """跳过注释（以#开头到行尾）"""
        while self.current_char and self.current_char != '\n':
            self.advance()
        if self.current_char == '\n':
            self.advance()
    
    def read_string(self) -> str:
        """读取字符串字面量"""
        result = ''
        self.advance()  # 跳过开始的引号
        
        while self.current_char and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == '\\':
                    result += '\\'
                elif self.current_char == '"':
                    result += '"'
                else:
                    result += self.current_char
            else:
                result += self.current_char
            self.advance()
        
        if self.current_char != '"':
            self.error("Unterminated string")
        
        self.advance()  # 跳过结束的引号
        return result
    
    def read_number(self) -> str:
        """读取数字"""
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return result
    
    def read_identifier(self) -> str:
        """读取标识符"""
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result
    
    def peek(self, offset: int = 1) -> Optional[str]:
        """查看前方字符，不移动位置"""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def get_next_token(self) -> Token:
        """获取下一个Token"""
        while self.current_char:
            # 跳过空白
            if self.current_char in ' \t\r':
                self.skip_whitespace()
                continue
            
            # 跳过注释
            if self.current_char == '#':
                self.skip_comment()
                continue
            
            # 换行符
            if self.current_char == '\n':
                token = Token(TokenType.NEWLINE, '\n', self.line, self.column)
                self.advance()
                return token
            
            # 字符串
            if self.current_char == '"':
                line, col = self.line, self.column
                value = self.read_string()
                return Token(TokenType.STRING, value, line, col)
            
            # 数字
            if self.current_char.isdigit():
                line, col = self.line, self.column
                value = self.read_number()
                return Token(TokenType.NUMBER, value, line, col)
            
            # 标识符或关键字
            if self.current_char.isalpha() or self.current_char == '_':
                line, col = self.line, self.column
                value = self.read_identifier()
                token_type = self.KEYWORDS.get(value, TokenType.IDENTIFIER)
                return Token(token_type, value, line, col)
            
            # 特殊字符
            line, col = self.line, self.column
            char = self.current_char
            
            if char == '{':
                self.advance()
                return Token(TokenType.LBRACE, char, line, col)
            elif char == '}':
                self.advance()
                return Token(TokenType.RBRACE, char, line, col)
            elif char == '(':
                self.advance()
                return Token(TokenType.LPAREN, char, line, col)
            elif char == ')':
                self.advance()
                return Token(TokenType.RPAREN, char, line, col)
            elif char == '[':
                self.advance()
                return Token(TokenType.LBRACKET, char, line, col)
            elif char == ']':
                self.advance()
                return Token(TokenType.RBRACKET, char, line, col)
            elif char == '=':
                self.advance()
                return Token(TokenType.EQUALS, char, line, col)
            elif char == ',':
                self.advance()
                return Token(TokenType.COMMA, char, line, col)
            elif char == '$':
                self.advance()
                return Token(TokenType.DOLLAR, char, line, col)
            else:
                self.error(f"Unexpected character: {char}")
        
        return Token(TokenType.EOF, '', self.line, self.column)
    
    def tokenize(self) -> List[Token]:
        """将整个源代码转换为Token列表"""
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens

