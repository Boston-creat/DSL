# 日志格式说明文档

## 1. 概述

本项目使用Python标准库`logging`模块实现日志功能，记录系统运行过程中的关键信息，包括系统启动、脚本加载、意图识别、错误处理等。

## 2. 日志文件位置

- **日志目录**: `logs/`（项目根目录下）
- **日志文件命名**: `dsl_agent_YYYYMMDD.log`（按日期命名）
- **示例**: `logs/dsl_agent_20250116.log`

## 3. 日志文件管理

- **文件大小限制**: 每个日志文件最大10MB
- **文件轮转**: 当日志文件达到10MB时，自动创建新文件
- **备份数量**: 保留最近5个备份文件
- **备份文件命名**: `dsl_agent_YYYYMMDD.log.1`, `dsl_agent_YYYYMMDD.log.2`, 等

## 4. 日志格式

### 4.1 标准格式

```
时间戳 | 日志级别 | 记录器名称 | 文件名:行号 | 消息内容
```

### 4.2 格式说明

- **时间戳**: `YYYY-MM-DD HH:MM:SS` 格式，精确到秒
- **日志级别**: 8个字符宽度，左对齐
  - `DEBUG` - 调试信息
  - `INFO` - 一般信息
  - `WARNING` - 警告信息
  - `ERROR` - 错误信息
  - `CRITICAL` - 严重错误
- **记录器名称**: 标识日志来源模块
  - `DSL_Agent_CLI` - 命令行界面
  - `DSL_Agent_GUI` - 图形界面
  - `DSL_Agent_Interpreter` - 解释器
  - `DSL_Agent_LLM` - LLM客户端
- **文件名:行号**: 记录日志产生的代码位置
- **消息内容**: 具体的日志信息

### 4.3 格式示例

```
2025-01-16 14:30:25 | INFO     | DSL_Agent_CLI | cli.py:45 | 脚本文件路径: scripts/order_query.dsl
2025-01-16 14:30:25 | INFO     | DSL_Agent_CLI | cli.py:79 | 开始加载DSL脚本文件: scripts/order_query.dsl
2025-01-16 14:30:25 | INFO     | DSL_Agent_CLI | cli.py:81 | 成功加载脚本文件，文件大小: 256 字符
2025-01-16 14:30:25 | INFO     | DSL_Agent_CLI | cli.py:88 | 开始词法分析
2025-01-16 14:30:25 | INFO     | DSL_Agent_CLI | cli.py:90 | 词法分析完成，共生成 45 个Token
2025-01-16 14:30:25 | INFO     | DSL_Agent_CLI | cli.py:97 | 开始语法分析
2025-01-16 14:30:25 | INFO     | DSL_Agent_CLI | cli.py:99 | 语法分析完成，共解析出 1 个意图
2025-01-16 14:30:25 | INFO     | DSL_Agent_LLM | llm_client.py:42 | 初始化智谱AI客户端，模型: glm-4
2025-01-16 14:30:25 | INFO     | DSL_Agent_LLM | llm_client.py:58 | 智谱AI客户端初始化成功
2025-01-16 14:30:25 | INFO     | DSL_Agent_CLI | cli.py:107 | LLM客户端初始化成功
2025-01-16 14:30:25 | INFO     | DSL_Agent_Interpreter | interpreter.py:78 | 创建解释器实例
2025-01-16 14:30:25 | INFO     | DSL_Agent_CLI | cli.py:123 | 系统初始化完成，进入交互模式
2025-01-16 14:30:30 | INFO     | DSL_Agent_CLI | cli.py:135 | 收到用户输入: 查询订单
2025-01-16 14:30:30 | DEBUG    | DSL_Agent_Interpreter | interpreter.py:87 | 开始匹配意图，用户输入: 查询订单
2025-01-16 14:30:30 | DEBUG    | DSL_Agent_LLM | llm_client.py:67 | 开始意图识别，用户输入: 查询订单...
2025-01-16 14:30:30 | DEBUG    | DSL_Agent_LLM | llm_client.py:88 | 调用智谱AI API进行意图识别
2025-01-16 14:30:32 | INFO     | DSL_Agent_LLM | llm_client.py:95 | LLM返回的意图名称: 订单查询
2025-01-16 14:30:32 | INFO     | DSL_Agent_LLM | llm_client.py:103 | 验证通过，匹配到意图: 订单查询
2025-01-16 14:30:32 | INFO     | DSL_Agent_Interpreter | interpreter.py:95 | LLM识别到意图: 订单查询
2025-01-16 14:30:32 | INFO     | DSL_Agent_CLI | cli.py:153 | 识别到意图: 订单查询
2025-01-16 14:30:32 | INFO     | DSL_Agent_Interpreter | interpreter.py:125 | 开始执行意图: 订单查询，动作数量: 3
2025-01-16 14:30:32 | DEBUG    | DSL_Agent_Interpreter | interpreter.py:140 | 执行动作 1/3: AskAction
2025-01-16 14:30:32 | DEBUG    | DSL_Agent_Interpreter | interpreter.py:140 | 执行动作 2/3: WaitForAction
2025-01-16 14:30:35 | DEBUG    | DSL_Agent_Interpreter | interpreter.py:140 | 执行动作 3/3: ResponseAction
2025-01-16 14:30:35 | INFO     | DSL_Agent_Interpreter | interpreter.py:151 | 意图执行完成: 订单查询
```

## 5. 日志级别说明

### 5.1 DEBUG（调试）
记录详细的调试信息，用于开发阶段的问题定位。

**记录内容**:
- 函数调用流程
- 变量值
- 中间处理步骤
- API调用详情

**示例**:
```
2025-01-16 14:30:30 | DEBUG    | DSL_Agent_Interpreter | interpreter.py:87 | 开始匹配意图，用户输入: 查询订单
2025-01-16 14:30:30 | DEBUG    | DSL_Agent_Interpreter | interpreter.py:89 | 对话历史长度: 1
```

### 5.2 INFO（信息）
记录系统正常运行的关键信息。

**记录内容**:
- 系统启动和关闭
- 脚本加载成功
- 意图识别结果
- 意图执行完成
- 用户操作

**示例**:
```
2025-01-16 14:30:25 | INFO     | DSL_Agent_CLI | cli.py:45 | 脚本文件路径: scripts/order_query.dsl
2025-01-16 14:30:32 | INFO     | DSL_Agent_Interpreter | interpreter.py:95 | LLM识别到意图: 订单查询
```

### 5.3 WARNING（警告）
记录可能的问题，但不影响系统运行。

**记录内容**:
- 配置缺失
- 意图识别失败
- 非关键错误

**示例**:
```
2025-01-16 14:30:30 | WARNING  | DSL_Agent_Interpreter | interpreter.py:100 | LLM未识别到任何意图
2025-01-16 14:30:30 | WARNING  | DSL_Agent_CLI | cli.py:144 | 未能识别用户意图，输入: 你好
```

### 5.4 ERROR（错误）
记录错误信息，可能影响功能。

**记录内容**:
- 文件读取失败
- API调用失败
- 语法错误
- 初始化失败

**示例**:
```
2025-01-16 14:30:25 | ERROR    | DSL_Agent_CLI | cli.py:27 | 文件不存在: scripts/invalid.dsl
2025-01-16 14:30:25 | ERROR    | DSL_Agent_LLM | llm_client.py:62 | 智谱AI客户端初始化失败: Invalid API key
```

### 5.5 CRITICAL（严重错误）
记录严重错误，可能导致系统无法运行。

**记录内容**:
- 系统崩溃
- 关键组件初始化失败

## 6. 日志记录器

### 6.1 CLI日志记录器
- **名称**: `DSL_Agent_CLI`
- **用途**: 记录命令行界面的操作
- **主要记录**:
  - 脚本加载
  - 词法/语法分析
  - 用户输入
  - 意图识别结果

### 6.2 GUI日志记录器
- **名称**: `DSL_Agent_GUI`
- **用途**: 记录图形界面的操作
- **主要记录**:
  - 界面启动
  - 脚本加载
  - 用户交互

### 6.3 解释器日志记录器
- **名称**: `DSL_Agent_Interpreter`
- **用途**: 记录解释器执行过程
- **主要记录**:
  - 意图匹配
  - 动作执行
  - 变量管理
  - 对话历史

### 6.4 LLM客户端日志记录器
- **名称**: `DSL_Agent_LLM`
- **用途**: 记录LLM API调用
- **主要记录**:
  - 客户端初始化
  - API调用
  - 意图识别结果
  - API错误

## 7. 日志输出位置

### 7.1 文件输出
所有日志都会写入到日志文件中，便于后续分析和问题追踪。

### 7.2 控制台输出
在CLI模式下，日志也会输出到控制台，方便实时查看。

### 7.3 GUI模式
在GUI模式下，日志仅写入文件，不显示在界面上。

## 8. 日志使用示例

### 8.1 查看当日日志
```bash
# Windows
type logs\dsl_agent_20250116.log

# Linux/Mac
cat logs/dsl_agent_20250116.log
```

### 8.2 查看错误日志
```bash
# Windows PowerShell
Select-String -Path "logs\*.log" -Pattern "ERROR"

# Linux/Mac
grep "ERROR" logs/*.log
```

### 8.3 查看特定模块日志
```bash
# 查看CLI相关日志
grep "DSL_Agent_CLI" logs/*.log

# 查看LLM相关日志
grep "DSL_Agent_LLM" logs/*.log
```

## 9. 日志配置

日志配置在 `src/logger.py` 中，可以通过修改以下参数调整日志行为：

- **日志级别**: 默认 `logging.INFO`，可改为 `logging.DEBUG` 查看更详细信息
- **文件大小**: 默认 10MB，可在 `RotatingFileHandler` 中修改 `maxBytes`
- **备份数量**: 默认 5个，可在 `RotatingFileHandler` 中修改 `backupCount`
- **日志格式**: 可在 `Formatter` 中自定义格式

## 10. 注意事项

1. **日志文件大小**: 日志文件会自动轮转，但建议定期清理旧日志文件
2. **敏感信息**: 日志中可能包含用户输入，注意保护隐私
3. **性能影响**: 日志记录对性能影响很小，但大量DEBUG日志可能影响性能
4. **编码**: 日志文件使用UTF-8编码，支持中文

## 11. 日志分析建议

1. **错误追踪**: 使用 `ERROR` 级别日志快速定位问题
2. **性能分析**: 通过时间戳分析操作耗时
3. **用户行为**: 通过 `INFO` 级别日志分析用户使用模式
4. **调试问题**: 启用 `DEBUG` 级别查看详细执行流程

---

**文档版本**: 1.0  
**最后更新**: 2025-01-16

