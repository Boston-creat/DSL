"""
解释器（Interpreter）
作用：遍历AST并执行相应的动作，实现DSL脚本的运行时行为
在全项目中的作用：这是编译过程的第三步，将AST转换为实际的执行逻辑，处理用户交互、变量管理和函数调用
"""

from typing import Dict, Any, Callable, Optional
from src.parser import (
    Program, IntentDecl, WhenClause, Action, AskAction, WaitForAction,
    ResponseAction, SetAction, OptionsAction, Expression, StringLiteral,
    Variable, FunctionCall
)


class Interpreter:
    """解释器"""
    
    def __init__(self, llm_client=None):
        """
        初始化解释器
        :param llm_client: LLM客户端实例，用于意图识别
        """
        self.llm_client = llm_client
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Callable] = {
            'get_order_status': self._get_order_status,
            'create_refund': self._create_refund,
            'create_ticket': self._create_ticket,
        }
        self.current_intent: Optional[IntentDecl] = None
        self.user_input_callback: Optional[Callable[[str], str]] = None
    
    def set_user_input_callback(self, callback: Callable[[str], str]):
        """设置用户输入回调函数"""
        self.user_input_callback = callback
    
    def interpret(self, program: Program) -> Dict[str, Any]:
        """
        解释执行程序
        :param program: 程序AST
        :return: 执行结果
        """
        self.variables.clear()
        result = {
            'matched_intent': None,
            'response': None,
            'variables': {}
        }
        
        # 存储所有意图，供意图识别使用
        self.intents = program.intents
        
        return result
    
    def match_intent(self, user_input: str) -> Optional[IntentDecl]:
        """
        匹配用户输入的意图
        :param user_input: 用户输入
        :return: 匹配的意图，如果没有匹配则返回None
        """
        # 检查intents是否已设置
        if not hasattr(self, 'intents') or not self.intents:
            return None
        
        if not self.llm_client:
            # 如果没有LLM客户端，使用简单的关键词匹配
            return self._simple_match(user_input)
        
        # 使用LLM进行意图识别
        try:
            intent_name = self.llm_client.identify_intent(user_input, self.intents)
            if intent_name:
                for intent in self.intents:
                    if intent.name == intent_name:
                        return intent
            # 如果LLM返回None或空字符串，fallback到简单匹配
            # 注意：即使LLM返回None，也要fallback到简单匹配
            fallback_result = self._simple_match(user_input)
            return fallback_result
        except Exception as e:
            # LLM失败时fallback到简单匹配
            fallback_result = self._simple_match(user_input)
            return fallback_result
    
    def _simple_match(self, user_input: str) -> Optional[IntentDecl]:
        """简单的关键词匹配（备用方案）"""
        if not hasattr(self, 'intents') or not self.intents:
            return None
        
        user_input_lower = user_input.lower().strip()
        
        # 首先尝试完全匹配或包含匹配
        for intent in self.intents:
            if hasattr(intent, 'when_clause') and hasattr(intent.when_clause, 'patterns'):
                for pattern in intent.when_clause.patterns:
                    pattern_lower = pattern.lower().strip()
                    # 完全匹配或包含匹配
                    if pattern_lower == user_input_lower or pattern_lower in user_input_lower or user_input_lower in pattern_lower:
                        return intent
        
        # 如果完全匹配失败，尝试关键词匹配（提取关键词）
        # 对于中文，按字符分割而不是按空格
        import re
        # 提取中文字符和英文单词
        # 对于单个中文字符，也要提取
        user_keywords = set(re.findall(r'[\u4e00-\u9fa5]|[a-zA-Z]+', user_input_lower))
        if not user_keywords:
            return None
        
        best_match = None
        best_score = 0
        
        for intent in self.intents:
            if hasattr(intent, 'when_clause') and hasattr(intent.when_clause, 'patterns'):
                for pattern in intent.when_clause.patterns:
                    pattern_lower = pattern.lower().strip()
                    # 同样提取单个中文字符
                    pattern_keywords = set(re.findall(r'[\u4e00-\u9fa5]|[a-zA-Z]+', pattern_lower))
                    # 计算共同关键词数量
                    common_keywords = user_keywords & pattern_keywords
                    score = len(common_keywords)
                    if score > best_score:
                        best_score = score
                        best_match = intent
        
        return best_match if best_score > 0 else None
    
    def execute_intent(self, intent: IntentDecl) -> Dict[str, Any]:
        """
        执行意图
        :param intent: 意图声明
        :return: 执行结果
        """
        self.current_intent = intent
        self.variables.clear()
        result = {
            'response': None,
            'variables': {}
        }
        
        # 执行所有动作
        for action in intent.actions:
            action_result = self.execute_action(action)
            if action_result and 'response' in action_result:
                result['response'] = action_result['response']
            if action_result and 'variables' in action_result:
                result['variables'].update(action_result['variables'])
        
        return result
    
    def execute_action(self, action: Action) -> Optional[Dict[str, Any]]:
        """执行动作"""
        if isinstance(action, AskAction):
            return self.execute_ask(action)
        elif isinstance(action, WaitForAction):
            return self.execute_wait_for(action)
        elif isinstance(action, ResponseAction):
            return self.execute_response(action)
        elif isinstance(action, SetAction):
            return self.execute_set(action)
        elif isinstance(action, OptionsAction):
            return self.execute_options(action)
        return None
    
    def execute_ask(self, action: AskAction) -> Dict[str, Any]:
        """执行Ask动作"""
        print(f"[机器人] {action.message}")
        return {}
    
    def execute_wait_for(self, action: WaitForAction) -> Dict[str, Any]:
        """执行WaitFor动作"""
        if self.user_input_callback:
            user_input = self.user_input_callback(action.variable)
            self.variables[action.variable] = user_input
            return {'variables': {action.variable: user_input}}
        else:
            # 如果没有回调，使用标准输入
            user_input = input(f"请输入 {action.variable}: ")
            self.variables[action.variable] = user_input
            return {'variables': {action.variable: user_input}}
    
    def execute_response(self, action: ResponseAction) -> Dict[str, Any]:
        """执行Response动作"""
        response = self._format_template(action.template)
        print(f"[机器人] {response}")
        return {'response': response}
    
    def execute_set(self, action: SetAction) -> Dict[str, Any]:
        """执行Set动作"""
        value = self.evaluate_expression(action.expression)
        self.variables[action.variable] = value
        return {'variables': {action.variable: value}}
    
    def execute_options(self, action: OptionsAction) -> Dict[str, Any]:
        """执行Options动作"""
        print("请选择：")
        for i, option in enumerate(action.options, 1):
            print(f"  {i}. {option}")
        return {}
    
    def evaluate_expression(self, expr: Expression) -> Any:
        """求值表达式"""
        if isinstance(expr, StringLiteral):
            return expr.value
        elif isinstance(expr, Variable):
            return self.variables.get(expr.name, f"${expr.name}")
        elif isinstance(expr, FunctionCall):
            return self.evaluate_function_call(expr)
        else:
            return str(expr)
    
    def evaluate_function_call(self, call: FunctionCall) -> Any:
        """求值函数调用"""
        func = self.functions.get(call.name)
        if not func:
            # 如果函数不存在，返回一个模拟值
            return f"{call.name}({', '.join(str(self.evaluate_expression(arg)) for arg in call.args)})"
        
        args = [self.evaluate_expression(arg) for arg in call.args]
        return func(*args)
    
    def _format_template(self, template: str) -> str:
        """格式化模板字符串，替换变量和表达式"""
        import re
        
        def replace_expr(match):
            """替换匹配的表达式"""
            expr_str = match.group(1)  # 获取 { } 中的内容
            
            # 首先尝试作为变量名
            if expr_str in self.variables:
                return str(self.variables[expr_str])
            
            # 如果不是变量，尝试解析为表达式（函数调用等）
            try:
                # 尝试解析为函数调用，例如 get_order_status(order_number)
                # 简单的函数调用解析
                if '(' in expr_str and ')' in expr_str:
                    func_match = re.match(r'(\w+)\s*\((.*)\)', expr_str)
                    if func_match:
                        func_name = func_match.group(1)
                        args_str = func_match.group(2).strip()
                        
                        # 解析参数
                        args = []
                        if args_str:
                            # 简单的参数解析（支持变量名）
                            for arg in args_str.split(','):
                                arg = arg.strip()
                                # 如果是变量，获取变量值
                                if arg in self.variables:
                                    args.append(self.variables[arg])
                                else:
                                    # 否则作为字符串字面量
                                    args.append(arg)
                        
                        # 调用函数
                        if func_name in self.functions:
                            result = self.functions[func_name](*args)
                            return str(result)
                
                # 如果无法解析，返回原始表达式
                return match.group(0)
            except Exception as e:
                # 如果解析失败，返回原始表达式
                return match.group(0)
        
        # 使用正则表达式找到所有 {expression} 并替换
        pattern = r'\{([^}]+)\}'
        result = re.sub(pattern, replace_expr, template)
        return result
    
    # 内置函数实现
    def _get_order_status(self, order_number: str) -> str:
        """获取订单状态（模拟）"""
        # 实际应用中，这里应该调用真实的API或数据库
        return f"已发货"
    
    def _create_refund(self, order_number: str, reason: str) -> str:
        """创建退款申请（模拟）"""
        # 实际应用中，这里应该调用真实的API
        refund_id = f"REF{order_number[-4:]}{len(reason)}"
        return refund_id
    
    def _create_ticket(self, description: str) -> str:
        """创建工单（模拟）"""
        # 实际应用中，这里应该调用真实的API
        ticket_id = f"TICKET{hash(description) % 10000:04d}"
        return ticket_id

