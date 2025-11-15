"""
LLM客户端测试桩（Mock）
作用：模拟LLM API调用，用于测试时避免真实API调用
在全项目中的作用：这是测试桩，用于隔离测试，确保测试不依赖外部服务，提高测试的稳定性和速度
"""

from typing import List, Optional
from src.llm_client import LLMClient


class MockLLMClient(LLMClient):
    """Mock LLM客户端，用于测试"""
    
    def __init__(self, intent_mapping: dict = None):
        """
        初始化Mock客户端
        :param intent_mapping: 用户输入到意图名称的映射字典
        """
        self.intent_mapping = intent_mapping or {}
        self.call_history = []  # 记录所有调用历史
    
    def identify_intent(self, user_input: str, intents: List) -> Optional[str]:
        """
        模拟意图识别
        :param user_input: 用户输入
        :param intents: 可用意图列表
        :return: 匹配的意图名称
        """
        # 记录调用
        self.call_history.append({
            'user_input': user_input,
            'available_intents': [intent.name for intent in intents]
        })
        
        # 如果提供了映射，使用映射
        if self.intent_mapping:
            for pattern, intent_name in self.intent_mapping.items():
                if pattern.lower() in user_input.lower():
                    # 验证意图是否存在
                    for intent in intents:
                        if intent.name == intent_name:
                            return intent_name
            return None
        
        # 否则使用简单的关键词匹配
        user_input_lower = user_input.lower()
        for intent in intents:
            for pattern in intent.when_clause.patterns:
                if pattern.lower() in user_input_lower:
                    return intent.name
        
        return None
    
    def get_call_count(self) -> int:
        """获取调用次数"""
        return len(self.call_history)
    
    def get_last_call(self) -> dict:
        """获取最后一次调用信息"""
        return self.call_history[-1] if self.call_history else None


class FailingLLMClient(LLMClient):
    """模拟失败的LLM客户端，用于测试错误处理"""
    
    def identify_intent(self, user_input: str, intents: List) -> Optional[str]:
        """模拟API调用失败"""
        raise Exception("模拟的LLM API调用失败")

