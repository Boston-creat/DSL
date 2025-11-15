"""
语法分析器（Parser）
作用：根据词法分析器产生的Token序列，构建抽象语法树（AST）
在全项目中的作用：这是编译过程的第二步，将线性的Token序列转换为树形结构，为解释器提供执行依据
"""

from typing import List, Optional, Any
from src.lexer import Lexer, Token, TokenType


class ASTNode:
    """AST节点基类"""
    def __repr__(self):
        return f"{self.__class__.__name__}()"


class Program(ASTNode):
    """程序节点：包含多个意图声明"""
    def __init__(self, intents: List['IntentDecl']):
        self.intents = intents
    
    def __repr__(self):
        return f"Program({len(self.intents)} intents)"


class IntentDecl(ASTNode):
    """意图声明节点"""
    def __init__(self, name: str, when_clause: 'WhenClause', actions: List['Action']):
        self.name = name
        self.when_clause = when_clause
        self.actions = actions
    
    def __repr__(self):
        return f"IntentDecl({self.name!r}, {len(self.actions)} actions)"


class WhenClause(ASTNode):
    """When子句节点"""
    def __init__(self, patterns: List[str]):
        self.patterns = patterns
    
    def __repr__(self):
        return f"WhenClause({self.patterns})"


class Action(ASTNode):
    """动作节点基类"""
    pass


class AskAction(Action):
    """Ask动作节点"""
    def __init__(self, message: str):
        self.message = message
    
    def __repr__(self):
        return f"AskAction({self.message!r})"


class WaitForAction(Action):
    """WaitFor动作节点"""
    def __init__(self, variable: str):
        self.variable = variable
    
    def __repr__(self):
        return f"WaitForAction({self.variable})"


class ResponseAction(Action):
    """Response动作节点"""
    def __init__(self, template: str):
        self.template = template
    
    def __repr__(self):
        return f"ResponseAction({self.template!r})"


class SetAction(Action):
    """Set动作节点"""
    def __init__(self, variable: str, expression: 'Expression'):
        self.variable = variable
        self.expression = expression
    
    def __repr__(self):
        return f"SetAction({self.variable}, {self.expression})"


class OptionsAction(Action):
    """Options动作节点"""
    def __init__(self, options: List[str]):
        self.options = options
    
    def __repr__(self):
        return f"OptionsAction({self.options})"


class Expression(ASTNode):
    """表达式节点基类"""
    pass


class StringLiteral(Expression):
    """字符串字面量"""
    def __init__(self, value: str):
        self.value = value
    
    def __repr__(self):
        return f"StringLiteral({self.value!r})"


class Variable(Expression):
    """变量引用"""
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"Variable({self.name})"


class FunctionCall(Expression):
    """函数调用"""
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args
    
    def __repr__(self):
        return f"FunctionCall({self.name}, {len(self.args)} args)"


class Parser:
    """语法分析器"""
    
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.tokens = lexer.tokenize()
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
    
    def error(self, message: str):
        """抛出语法分析错误"""
        if self.current_token:
            raise SyntaxError(
                f"Parser error at line {self.current_token.line}, "
                f"column {self.current_token.column}: {message}"
            )
        else:
            raise SyntaxError(f"Parser error: {message}")
    
    def advance(self):
        """移动到下一个Token"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def expect(self, token_type: TokenType):
        """期望当前Token是指定类型，否则报错"""
        if not self.current_token or self.current_token.type != token_type:
            expected = token_type.name
            got = self.current_token.type.name if self.current_token else "EOF"
            self.error(f"Expected {expected}, got {got}")
        value = self.current_token.value
        self.advance()
        return value
    
    def skip_newlines(self):
        """跳过换行符"""
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> Program:
        """解析程序"""
        intents = []
        self.skip_newlines()
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.INTENT:
                intent = self.parse_intent()
                intents.append(intent)
            else:
                # 跳过注释行（以#开头的行）
                if self.current_token.value and self.current_token.value.strip().startswith('#'):
                    # 跳过到下一行
                    while self.current_token and self.current_token.type != TokenType.NEWLINE and self.current_token.type != TokenType.EOF:
                        self.advance()
                    self.skip_newlines()
                    continue
                self.error(f"Unexpected token: {self.current_token.type}")
            self.skip_newlines()
        
        return Program(intents)
    
    def parse_intent(self) -> IntentDecl:
        """解析意图声明"""
        self.expect(TokenType.INTENT)
        name = self.expect(TokenType.STRING)
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        when_clause = self.parse_when_clause()
        self.skip_newlines()
        
        actions = []
        # 解析when_clause内部的actions（直到when_clause的RBRACE）
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            action = self.parse_action()
            actions.append(action)
            self.skip_newlines()
        
        # 跳过when_clause的RBRACE
        self.expect(TokenType.RBRACE)
        self.skip_newlines()
        
        # 跳过intent的RBRACE
        self.expect(TokenType.RBRACE)
        return IntentDecl(name, when_clause, actions)
    
    def parse_when_clause(self) -> WhenClause:
        """解析When子句"""
        self.expect(TokenType.WHEN)
        self.expect(TokenType.USER_SAYS)
        
        patterns = []
        patterns.append(self.expect(TokenType.STRING))
        
        while self.current_token and self.current_token.type == TokenType.OR:
            self.advance()  # 跳过 'or'
            patterns.append(self.expect(TokenType.STRING))
        
        self.expect(TokenType.LBRACE)
        return WhenClause(patterns)
    
    def parse_action(self) -> Action:
        """解析动作"""
        if self.current_token.type == TokenType.ASK:
            return self.parse_ask_action()
        elif self.current_token.type == TokenType.WAIT_FOR:
            return self.parse_wait_for_action()
        elif self.current_token.type == TokenType.RESPONSE:
            return self.parse_response_action()
        elif self.current_token.type == TokenType.SET:
            return self.parse_set_action()
        elif self.current_token.type == TokenType.OPTIONS:
            return self.parse_options_action()
        else:
            self.error(f"Unexpected action: {self.current_token.type}")
    
    def parse_ask_action(self) -> AskAction:
        """解析Ask动作"""
        self.expect(TokenType.ASK)
        message = self.expect(TokenType.STRING)
        return AskAction(message)
    
    def parse_wait_for_action(self) -> WaitForAction:
        """解析WaitFor动作"""
        self.expect(TokenType.WAIT_FOR)
        variable = self.expect(TokenType.IDENTIFIER)
        return WaitForAction(variable)
    
    def parse_response_action(self) -> ResponseAction:
        """解析Response动作"""
        self.expect(TokenType.RESPONSE)
        template = self.expect(TokenType.STRING)
        return ResponseAction(template)
    
    def parse_set_action(self) -> SetAction:
        """解析Set动作"""
        self.expect(TokenType.SET)
        variable = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.EQUALS)
        expression = self.parse_expression()
        return SetAction(variable, expression)
    
    def parse_options_action(self) -> OptionsAction:
        """解析Options动作"""
        self.expect(TokenType.OPTIONS)
        self.expect(TokenType.LBRACKET)
        
        options = []
        if self.current_token.type == TokenType.STRING:
            options.append(self.expect(TokenType.STRING))
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                options.append(self.expect(TokenType.STRING))
        
        self.expect(TokenType.RBRACKET)
        return OptionsAction(options)
    
    def parse_expression(self) -> Expression:
        """解析表达式"""
        if self.current_token.type == TokenType.STRING:
            value = self.expect(TokenType.STRING)
            return StringLiteral(value)
        elif self.current_token.type == TokenType.IDENTIFIER:
            name = self.expect(TokenType.IDENTIFIER)
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                # 函数调用
                self.advance()
                args = []
                if self.current_token.type != TokenType.RPAREN:
                    args.append(self.parse_expression())
                    while self.current_token.type == TokenType.COMMA:
                        self.advance()
                        args.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                return FunctionCall(name, args)
            else:
                # 变量引用
                return Variable(name)
        elif self.current_token.type == TokenType.DOLLAR:
            self.advance()
            name = self.expect(TokenType.IDENTIFIER)
            return Variable(name)
        else:
            self.error(f"Unexpected expression token: {self.current_token.type}")

