"""
LLM客户端（LLM Client）
作用：封装大语言模型API调用，实现用户输入的意图识别
在全项目中的作用：这是AI能力集成模块，将自然语言输入转换为DSL脚本可以理解的意图，体现了传统规则引擎与AI技术的融合
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class LLMClient:
    """LLM客户端基类"""
    
    def identify_intent(self, user_input: str, intents: List) -> Optional[str]:
        """
        识别用户输入的意图
        :param user_input: 用户输入的自然语言
        :param intents: 可用的意图列表
        :return: 匹配的意图名称，如果没有匹配则返回None
        """
        raise NotImplementedError


class ZhipuAIClient(LLMClient):
    """智谱AI (GLM) API客户端 - 中国可用"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "glm-4"):
        """
        初始化智谱AI客户端
        :param api_key: 智谱AI API密钥，如果不提供则从环境变量读取
        :param model: 使用的模型名称 (glm-4, glm-3-turbo等)
        """
        api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
        
        # 如果没有API Key，不抛出异常，而是设置client为None，让identify_intent返回None，fallback到简单匹配
        if not api_key:
            print("提示: 未配置ZHIPUAI_API_KEY，将使用简单匹配模式")
            self.client = None
            self.model = model
            return
        
        try:
            import zhipuai
            self.client = zhipuai.ZhipuAI(api_key=api_key)
            self.model = model
        except ImportError:
            print("警告: 未安装zhipuai库，将使用简单匹配模式。安装方法: pip install zhipuai")
            self.client = None
            self.model = model
        except Exception as e:
            print(f"警告: 智谱AI客户端初始化失败: {e}，将使用简单匹配模式")
            self.client = None
            self.model = model
    
    def identify_intent(self, user_input: str, intents: List) -> Optional[str]:
        """使用智谱AI API识别意图"""
        # 如果客户端未初始化（没有API Key或初始化失败），返回None让解释器fallback到简单匹配
        if not self.client:
            return None
        
        # 构建意图列表描述
        intent_descriptions = []
        for intent in intents:
            patterns = ", ".join(intent.when_clause.patterns)
            intent_descriptions.append(f"- {intent.name}: {patterns}")
        
        intent_list = "\n".join(intent_descriptions)
        
        # 构建提示词
        prompt = f"""你是一个智能客服系统的意图识别模块。请根据用户输入，从以下意图列表中选择最匹配的意图。

可用意图列表：
{intent_list}

用户输入：{user_input}

请只返回意图名称（不要包含引号或其他字符），如果没有匹配的意图，返回"None"。"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的意图识别助手，只返回意图名称。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            intent_name = response.choices[0].message.content.strip()
            
            # 验证返回的意图名称是否有效
            if intent_name == "None" or not intent_name:
                return None
            
            # 检查意图名称是否在列表中
            for intent in intents:
                if intent.name == intent_name:
                    return intent_name
            
            return None
        except Exception as e:
            print(f"智谱AI API调用失败: {e}")
            return None


class SimpleLLMClient(LLMClient):
    """简单的关键词匹配客户端（用于测试或备用）"""
    
    def identify_intent(self, user_input: str, intents: List) -> Optional[str]:
        """使用简单的关键词匹配识别意图"""
        user_input_lower = user_input.lower().strip()
        
        # 首先尝试完全匹配或包含匹配
        for intent in intents:
            for pattern in intent.when_clause.patterns:
                pattern_lower = pattern.lower().strip()
                # 完全匹配或包含匹配（双向）
                if pattern_lower == user_input_lower or pattern_lower in user_input_lower or user_input_lower in pattern_lower:
                    return intent.name
        
        # 如果完全匹配失败，尝试关键词匹配
        import re
        user_keywords = set(re.findall(r'[\u4e00-\u9fa5]|[a-zA-Z]+', user_input_lower))
        if not user_keywords:
            return None
        
        best_match = None
        best_score = 0
        
        for intent in intents:
            for pattern in intent.when_clause.patterns:
                pattern_lower = pattern.lower().strip()
                pattern_keywords = set(re.findall(r'[\u4e00-\u9fa5]|[a-zA-Z]+', pattern_lower))
                common_keywords = user_keywords & pattern_keywords
                score = len(common_keywords)
                if score > best_score:
                    best_score = score
                    best_match = intent
        
        return best_match.name if best_match and best_score > 0 else None


def create_llm_client(client_type: str = "zhipuai", **kwargs) -> LLMClient:
    """
    创建LLM客户端
    :param client_type: 客户端类型 ("zhipuai", "simple")
    :param kwargs: 客户端初始化参数
    :return: LLM客户端实例
    """
    if client_type == "zhipuai":
        try:
            return ZhipuAIClient(**kwargs)
        except Exception as e:
            print(f"无法创建智谱AI客户端，使用简单匹配: {e}")
            return SimpleLLMClient()
    elif client_type == "simple":
        return SimpleLLMClient()
    else:
        raise ValueError(f"未知的客户端类型: {client_type}，支持的类型: zhipuai, simple")

