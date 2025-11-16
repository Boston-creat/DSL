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
        :raises ValueError: 如果未配置API Key或初始化失败
        """
        api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
        
        # 如果没有API Key，抛出异常
        if not api_key:
            raise ValueError(
                "未配置ZHIPUAI_API_KEY。请配置API密钥：\n"
                "1. 创建 .env 文件\n"
                "2. 添加 ZHIPUAI_API_KEY=your_key\n"
                "3. 获取API密钥：访问 https://open.bigmodel.cn/"
            )
        
        try:
            import zhipuai
            self.client = zhipuai.ZhipuAI(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError(
                "未安装zhipuai库。请安装：pip install zhipuai\n"
                "本项目要求使用API进行意图识别，不支持简单匹配模式。"
            )
        except Exception as e:
            raise RuntimeError(f"智谱AI客户端初始化失败: {e}")
    
    def identify_intent(self, user_input: str, intents: List) -> Optional[str]:
        """使用智谱AI API识别意图"""
        # 确保客户端已初始化
        if not self.client:
            raise RuntimeError("智谱AI客户端未正确初始化")
        
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


def create_llm_client(client_type: str = "zhipuai", **kwargs) -> LLMClient:
    """
    创建LLM客户端
    :param client_type: 客户端类型（目前仅支持 "zhipuai"）
    :param kwargs: 客户端初始化参数
    :return: LLM客户端实例
    :raises ValueError: 如果客户端类型不支持
    """
    if client_type == "zhipuai":
        return ZhipuAIClient(**kwargs)
    else:
        raise ValueError(
            f"未知的客户端类型: {client_type}。\n"
            f"本项目要求使用API进行意图识别，仅支持: zhipuai（智谱AI）\n"
            f"请配置 ZHIPUAI_API_KEY 环境变量。"
        )

