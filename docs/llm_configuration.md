# LLM配置指南

## 当前配置状态

### ✅ 已实现的功能

1. **SimpleLLMClient（简单匹配）** - 默认使用
   - 不需要任何配置
   - 使用关键词匹配进行意图识别
   - 适合测试和演示

2. **OpenAIClient（OpenAI API）** - 可选
   - 需要配置API密钥
   - 使用GPT模型进行智能意图识别
   - 更准确的意图识别能力

## 使用方式

### 方式1：使用简单匹配（默认，无需配置）

```bash
# 直接运行，使用简单匹配
python src/cli.py scripts/order_query.dsl
```

### 方式2：使用OpenAI API（需要配置）

1. **创建 `.env` 文件**（在项目根目录）：
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

2. **获取OpenAI API密钥**：
   - 访问 https://platform.openai.com/api-keys
   - 注册账号并创建API密钥
   - 将密钥复制到 `.env` 文件中

3. **运行时指定使用OpenAI**：
   ```bash
   python src/cli.py scripts/order_query.dsl --llm-client openai
   ```

## 配置说明

### 环境变量

- `OPENAI_API_KEY`: OpenAI API密钥（必需，如果使用OpenAI）
- `OPENAI_MODEL`: 使用的模型名称（可选，默认：gpt-3.5-turbo）

### 命令行参数

- `--llm-client simple`: 使用简单匹配（默认）
- `--llm-client openai`: 使用OpenAI API

## 自动降级机制

如果配置了OpenAI但API调用失败，系统会自动降级到简单匹配，确保程序始终可用。

## 测试建议

- **开发测试**：使用 `simple` 模式，无需配置，快速测试
- **演示/答辩**：可以配置OpenAI，展示AI意图识别能力
- **测试用例**：使用Mock客户端，不依赖真实API

## 注意事项

1. `.env` 文件包含敏感信息，**不要提交到Git仓库**
2. 已在 `.gitignore` 中忽略 `.env` 文件
3. 使用OpenAI API会产生费用，请注意使用量
4. 如果没有API密钥，使用 `simple` 模式即可完成所有功能测试

