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
        except Exception as e:
            print(f"LLM意图识别失败，使用简单匹配: {e}")
            return self._simple_match(user_input)
        
        return None
    
    def _simple_match(self, user_input: str) -> Optional[IntentDecl]:
        """简单的关键词匹配（备用方案）"""
        user_input_lower = user_input.lower()
        for intent in self.intents:
            for pattern in intent.when_clause.patterns:
                if pattern.lower() in user_input_lower:
                    return intent
        return None
    
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
        print(f"🤖 {action.message}")
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
        print(f"🤖 {response}")
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
        """格式化模板字符串，替换变量"""
        result = template
        for var_name, var_value in self.variables.items():
            result = result.replace(f"{{{var_name}}}", str(var_value))
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

