# LLM功能要求符合性说明

## 作业要求

**程序功能基本要求第3条**：
> 选用一种开放API的大语言模型，调用其API对用户的非结构化输入进行意图识别。

## 实现情况

### ✅ 已完全实现

1. **选用的LLM API**：OpenAI GPT API
   - 使用 `gpt-3.5-turbo` 模型（可配置）
   - 通过官方 `openai` Python库调用
   - 支持环境变量配置API密钥

2. **意图识别功能**：
   - 实现位置：`src/llm_client.py` 中的 `OpenAIClient` 类
   - 核心方法：`identify_intent(user_input: str, intents: List) -> Optional[str]`
   - 功能：将用户的自然语言输入转换为DSL脚本中定义的意图名称

3. **集成到解释器**：
   - 解释器在 `match_intent()` 方法中调用LLM客户端
   - 如果LLM返回结果，直接使用；如果失败，自动降级到简单匹配
   - 位置：`src/interpreter.py` 第69-80行

4. **CLI集成**：
   - 默认尝试使用OpenAI API（如果配置了）
   - 支持命令行参数切换：`--llm-client openai` 或 `--llm-client simple`
   - 位置：`src/cli.py` 第44-56行

## 技术实现细节

### LLM API调用流程

```
用户输入自然语言
    ↓
CLI接收输入
    ↓
Interpreter.match_intent()
    ↓
LLMClient.identify_intent()
    ↓
构建提示词（包含所有可用意图）
    ↓
调用OpenAI API (gpt-3.5-turbo)
    ↓
解析返回的意图名称
    ↓
验证并返回匹配的意图
    ↓
执行对应的DSL脚本逻辑
```

### 提示词设计

系统会为每次意图识别构建如下提示词：

```
你是一个智能客服系统的意图识别模块。请根据用户输入，从以下意图列表中选择最匹配的意图。

可用意图列表：
- 订单查询: 查询订单, 我的订单, 订单状态, 查看订单
- 退款申请: 退款, 退货, 申请退款, 我要退款
- 技术支持: 故障, 问题, 无法使用, 需要帮助, 技术支持

用户输入：{用户实际输入}

请只返回意图名称（不要包含引号或其他字符），如果没有匹配的意图，返回"None"。
```

### 代码示例

**LLM客户端实现**（`src/llm_client.py`）：
```python
class OpenAIClient(LLMClient):
    def identify_intent(self, user_input: str, intents: List) -> Optional[str]:
        """使用OpenAI API识别意图"""
        # 构建意图列表描述
        intent_descriptions = []
        for intent in intents:
            patterns = ", ".join(intent.when_clause.patterns)
            intent_descriptions.append(f"- {intent.name}: {patterns}")
        
        # 构建提示词
        prompt = f"""你是一个智能客服系统的意图识别模块..."""
        
        # 调用OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[...],
            temperature=0.3,
            max_tokens=50
        )
        
        # 解析并验证返回结果
        intent_name = response.choices[0].message.content.strip()
        ...
```

**解释器集成**（`src/interpreter.py`）：
```python
def match_intent(self, user_input: str) -> Optional[IntentDecl]:
    """匹配用户输入的意图"""
    if not self.llm_client:
        return self._simple_match(user_input)
    
    # 使用LLM进行意图识别
    try:
        intent_name = self.llm_client.identify_intent(user_input, self.intents)
        if intent_name:
            for intent in self.intents:
                if intent.name == intent_name:
                    return intent
        # 如果LLM返回None，fallback到简单匹配
        return self._simple_match(user_input)
    except Exception as e:
        # LLM失败时fallback到简单匹配
        return self._simple_match(user_input)
```

## 配置和使用

### 1. 配置API密钥

创建 `.env` 文件：
```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 2. 运行程序

```bash
# 默认使用OpenAI（如果配置了）
python src/cli.py scripts/order_query.dsl

# 明确指定使用OpenAI
python src/cli.py scripts/order_query.dsl --llm-client openai
```

### 3. 验证LLM功能

运行程序后，输入自然语言，系统会：
1. 调用OpenAI API进行意图识别
2. 显示识别到的意图
3. 执行对应的DSL脚本逻辑

**示例交互**：
```
您: 我想查一下我的订单
[*] 识别意图中...
[OK] 识别到意图: 订单查询
[机器人] 请输入您的订单号
```

## 测试验证

### 测试用例

1. **测试LLM意图识别**（`tests/test_with_stubs.py`）：
   - 使用Mock LLM客户端测试意图识别流程
   - 验证LLM客户端被正确调用

2. **测试降级机制**：
   - 测试LLM失败时自动降级到简单匹配
   - 确保系统始终可用

### 测试结果

所有测试用例通过，包括：
- ✅ LLM客户端初始化测试
- ✅ 意图识别功能测试
- ✅ 降级机制测试
- ✅ 集成测试

## 符合性总结

| 要求项 | 实现情况 | 说明 |
|--------|---------|------|
| 选用开放API的大语言模型 | ✅ | 使用OpenAI GPT API |
| 调用API | ✅ | 通过官方openai库调用 |
| 对非结构化输入进行意图识别 | ✅ | 接收自然语言，返回意图名称 |
| 集成到系统 | ✅ | 完全集成到解释器流程中 |

## 演示建议

在答辩时，可以演示：

1. **配置LLM**：展示 `.env` 文件配置
2. **运行程序**：使用OpenAI模式运行
3. **输入自然语言**：如"我想查订单"、"我要退款"等
4. **展示识别结果**：系统正确识别意图并执行脚本
5. **对比简单匹配**：展示LLM相比简单匹配的优势

## 相关文件

- `src/llm_client.py` - LLM客户端实现
- `src/interpreter.py` - 解释器集成LLM
- `src/cli.py` - CLI集成
- `tests/stubs/mock_llm_client.py` - 测试桩
- `tests/test_with_stubs.py` - 测试用例
- `docs/llm_configuration.md` - 配置指南

