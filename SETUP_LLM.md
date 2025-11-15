# LLM API配置指南

## 智谱AI (GLM) - 中国可用 ✅ 推荐

### 1. 注册和获取API密钥

1. 访问 https://open.bigmodel.cn/
2. 注册/登录账号
3. 进入"控制台" -> "API Keys"
4. 创建新的API Key
5. 复制API Key（格式类似：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）

**注意**：智谱AI只需要一个API Key，配置简单！

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
ZHIPUAI_API_KEY=your_api_key_here
```

### 3. 安装依赖

```bash
pip install zhipuai
```

或安装所有依赖：

```bash
pip install -r requirements.txt
```

### 4. 使用

```bash
# 默认使用智谱AI
python src/cli.py scripts/order_query.dsl

# 或明确指定
python src/cli.py scripts/order_query.dsl --llm-client zhipuai
```

---

## 简单匹配模式（无需配置）

如果不想配置任何API，系统会自动使用简单匹配模式：

```bash
python src/cli.py scripts/order_query.dsl --llm-client simple
```

简单匹配模式使用关键词匹配进行意图识别，无需任何API配置。

---

## 快速测试

配置完成后，运行测试验证：

```bash
# 运行所有测试
python -m pytest tests/ -v

# 测试CLI
python src/cli.py scripts/order_query.dsl
```

## 故障排除

### 问题1：API密钥无效
- 检查密钥是否正确复制（不要有多余空格）
- 确认API密钥未过期
- 检查账户余额是否充足

### 问题2：网络连接问题
- 智谱AI在中国可直接访问
- 如果遇到网络问题，检查防火墙设置

### 问题3：依赖安装失败
```bash
# 单独安装
pip install zhipuai

# 如果pip安装慢，使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple zhipuai
```

### 问题4：自动降级
如果API调用失败，系统会自动降级到简单匹配模式，程序仍可正常运行。

---

## 支持的LLM类型

| 类型 | 命令参数 | 说明 | 需要配置 |
|------|---------|------|---------|
| 智谱AI | `zhipuai` | 默认，中国可用，推荐 | ✅ 只需API Key |
| 简单匹配 | `simple` | 关键词匹配 | ❌ 无需配置 |

---

## 使用示例

```bash
# 使用智谱AI（默认，如果已配置）
python src/cli.py scripts/order_query.dsl

# 明确指定使用智谱AI
python src/cli.py scripts/order_query.dsl --llm-client zhipuai

# 使用简单匹配（无需配置）
python src/cli.py scripts/order_query.dsl --llm-client simple
```

---

## 配置步骤总结

1. **注册智谱AI账号**：https://open.bigmodel.cn/
2. **获取API Key**：控制台 -> API Keys -> 创建密钥
3. **创建 `.env` 文件**，添加 `ZHIPUAI_API_KEY=your_key`
4. **安装依赖**：`pip install zhipuai`
5. **运行程序**：`python src/cli.py scripts/order_query.dsl`

完成！

---

## 为什么选择智谱AI？

- ✅ **中国可用**：无需翻墙，直接访问
- ✅ **配置简单**：只需一个API Key
- ✅ **稳定可靠**：API稳定，响应快速
- ✅ **免费额度**：新用户有免费额度
- ✅ **文档完善**：官方文档清晰
