# 基于DSL的多业务场景Agent的设计与实现

## 项目文档

**课程名称**：程序设计实践  
**学期**：2025年秋季学期  
**项目名称**：基于DSL的多业务场景Agent的设计与实现  
**作者**：[您的姓名]  
**日期**：[提交日期]

---

## 目录

1. [需求分析说明](#1-需求分析说明)
2. [概要设计说明](#2-概要设计说明)
3. [详细设计说明](#3-详细设计说明)
4. [测试报告](#4-测试报告)
5. [DSL脚本编写指南](#5-dsl脚本编写指南)
6. [AI辅助开发记录](#6-ai辅助开发记录)
7. [Git日志](#7-git日志)

---

## 1. 需求分析说明

### 1.1 项目背景

领域特定语言（DSL）是实现定制化业务流程的核心方法。本项目旨在设计一个能够描述特定领域的智能客服机器人的应答逻辑的脚本语言，并实现其解释器。通过集成大语言模型（LLM）API实现意图识别，驱动脚本的解释执行。

### 1.2 功能需求

#### 1.2.1 脚本语言设计
- **需求**：设计一种DSL，用于描述客服机器人的自动应答逻辑
- **要求**：语法可以自由定义，但语义上必须满足描述客服机器人自动应答逻辑的要求
- **实现**：设计了完整的DSL语法，支持意图定义、条件匹配、用户交互、响应生成等功能

#### 1.2.2 多业务场景支持
- **需求**：提供几种针对不同业务场景的脚本范例
- **要求**：不同脚本范例解释器执行后应有不同的行为表现
- **实现**：提供了4个业务场景脚本：
  - 订单查询场景（`scripts/order_query.dsl`）
  - 退款申请场景（`scripts/refund.dsl`）
  - 技术支持场景（`scripts/tech_support.dsl`）
  - 综合场景（`scripts/combined.dsl`）

#### 1.2.3 LLM意图识别
- **需求**：选用一种开放API的大语言模型，调用其API对用户的非结构化输入进行意图识别
- **要求**：能够处理自然语言输入，识别用户意图
- **实现**：集成OpenAI GPT API，实现智能意图识别功能

#### 1.2.4 用户界面
- **需求**：程序输入输出形式不限，可以简化为纯命令行界面
- **实现**：实现了完整的命令行界面（CLI），支持交互式操作

### 1.3 非功能需求

- **可扩展性**：模块化设计，易于扩展新功能
- **可测试性**：提供测试桩和测试驱动，支持自动化测试
- **可维护性**：代码结构清晰，文档完整
- **健壮性**：LLM失败时自动降级到简单匹配，确保系统可用

---

## 2. 概要设计说明

### 2.1 系统架构

系统采用经典的编译器架构，分为以下几个阶段：

```
用户输入（自然语言）
    ↓
[词法分析器] → Token序列
    ↓
[语法分析器] → AST（抽象语法树）
    ↓
[LLM客户端] → 意图识别
    ↓
[解释器] → 执行AST
    ↓
输出响应
```

### 2.2 模块划分

系统分为5个核心模块：

1. **词法分析模块** (`src/lexer.py`)
   - 职责：将DSL源代码转换为Token序列
   - 输入：DSL脚本源代码
   - 输出：Token列表

2. **语法分析模块** (`src/parser.py`)
   - 职责：将Token序列转换为AST
   - 输入：Token列表
   - 输出：AST（Program对象）

3. **解释器模块** (`src/interpreter.py`)
   - 职责：执行AST，处理用户交互
   - 输入：AST和用户输入
   - 输出：执行结果

4. **LLM客户端模块** (`src/llm_client.py`)
   - 职责：调用LLM API进行意图识别
   - 输入：用户自然语言输入和可用意图列表
   - 输出：匹配的意图名称

5. **CLI模块** (`src/cli.py`)
   - 职责：提供用户交互界面
   - 输入：DSL脚本文件路径
   - 输出：交互式命令行界面

### 2.3 数据流

1. 用户输入自然语言
2. CLI接收输入并加载DSL脚本
3. 词法分析器将脚本转换为Token序列
4. 语法分析器将Token序列转换为AST
5. LLM客户端识别用户意图
6. 解释器执行匹配的意图对应的动作
7. 输出响应给用户

---

## 3. 详细设计说明

### 3.1 数据结构设计

#### 3.1.1 Token类
```python
class Token:
    type: TokenType      # Token类型
    value: str           # Token值
    line: int            # 行号
    column: int          # 列号
```

#### 3.1.2 AST节点类

**Program**：程序根节点
```python
class Program(ASTNode):
    intents: List[IntentDecl]  # 意图声明列表
```

**IntentDecl**：意图声明
```python
class IntentDecl(ASTNode):
    name: str                  # 意图名称
    when_clause: WhenClause    # 条件子句
    actions: List[Action]      # 动作列表
```

**WhenClause**：条件子句
```python
class WhenClause(ASTNode):
    patterns: List[str]        # 匹配模式列表
```

**Action类族**：
- `AskAction`: 询问动作
- `WaitForAction`: 等待用户输入
- `ResponseAction`: 响应动作
- `SetAction`: 设置变量
- `OptionsAction`: 选项动作

**Expression类族**：
- `StringLiteral`: 字符串字面量
- `Variable`: 变量引用
- `FunctionCall`: 函数调用

### 3.2 模块接口详细定义

#### 3.2.1 词法分析器接口

**类名**：`Lexer`

**方法**：
```python
def tokenize(self) -> List[Token]
    """
    将源代码转换为Token序列
    返回: Token列表
    异常: SyntaxError - 词法分析错误
    """
```

**使用示例**：
```python
lexer = Lexer(script_content)
tokens = lexer.tokenize()
```

#### 3.2.2 语法分析器接口

**类名**：`Parser`

**方法**：
```python
def parse(self) -> Program
    """
    解析Token序列，构建AST
    返回: Program对象（AST根节点）
    异常: SyntaxError - 语法分析错误
    """
```

**使用示例**：
```python
parser = Parser(lexer)
program = parser.parse()
```

#### 3.2.3 解释器接口

**类名**：`Interpreter`

**方法**：
```python
def interpret(self, program: Program) -> Dict[str, Any]
    """
    解释执行程序
    参数: program - 程序AST
    返回: 执行结果字典
    """

def match_intent(self, user_input: str) -> Optional[IntentDecl]
    """
    匹配用户输入的意图
    参数: user_input - 用户输入的自然语言
    返回: 匹配的意图声明，如果没有匹配则返回None
    """

def execute_intent(self, intent: IntentDecl) -> Dict[str, Any]
    """
    执行意图
    参数: intent - 意图声明
    返回: 执行结果字典
    """
```

**使用示例**：
```python
interpreter = Interpreter(llm_client)
interpreter.interpret(program)
matched = interpreter.match_intent("查询订单")
if matched:
    result = interpreter.execute_intent(matched)
```

#### 3.2.4 LLM客户端接口

**基类**：`LLMClient`

**方法**：
```python
def identify_intent(self, user_input: str, intents: List) -> Optional[str]
    """
    识别用户输入的意图
    参数: 
        user_input - 用户输入的自然语言
        intents - 可用的意图列表
    返回: 匹配的意图名称，如果没有匹配则返回None
    """
```

**实现类**：
- `OpenAIClient`: OpenAI API客户端
- `SimpleLLMClient`: 简单匹配客户端（备用）

**工厂函数**：
```python
def create_llm_client(client_type: str = "openai", **kwargs) -> LLMClient
    """
    创建LLM客户端
    参数:
        client_type - 客户端类型 ("openai", "simple")
        kwargs - 客户端初始化参数
    返回: LLM客户端实例
    """
```

**使用示例**：
```python
llm_client = create_llm_client("openai")
intent_name = llm_client.identify_intent("查询订单", intents)
```

#### 3.2.5 CLI接口

**函数**：`main()`

**功能**：
- 解析命令行参数
- 加载DSL脚本文件
- 执行词法分析、语法分析
- 创建LLM客户端和解释器
- 提供交互式命令行界面

**命令行参数**：
```bash
python src/cli.py <script_file> [--llm-client <type>]
```

**使用示例**：
```bash
python src/cli.py scripts/order_query.dsl
python src/cli.py scripts/order_query.dsl --llm-client openai
```

### 3.3 关键算法设计

#### 3.3.1 词法分析算法
- 使用状态机模式识别Token
- 支持字符串字面量、标识符、关键字、运算符等
- 处理注释和空白字符

#### 3.3.2 语法分析算法
- 使用递归下降解析
- 支持错误恢复和错误报告
- 构建完整的AST结构

#### 3.3.3 意图匹配算法
- **LLM匹配**：调用OpenAI API进行智能识别
- **简单匹配**：三层匹配策略
  1. 完全匹配
  2. 包含匹配
  3. 关键词匹配（计算共同关键词数量）

#### 3.3.4 解释执行算法
- 遍历AST节点
- 执行对应的动作
- 管理变量作用域
- 处理函数调用

---

## 4. 测试报告

### 4.1 测试策略

采用单元测试、集成测试和端到端测试相结合的策略：

- **单元测试**：测试各个模块的独立功能
- **集成测试**：测试模块之间的协作
- **端到端测试**：测试完整的用户流程

### 4.2 测试桩设计

#### 4.2.1 MockLLMClient

**位置**：`tests/stubs/mock_llm_client.py`

**功能**：
- 模拟LLM API调用
- 支持预设的意图映射
- 记录调用历史

**设计说明**：
```python
class MockLLMClient(LLMClient):
    def __init__(self, intent_mapping: dict = None):
        """
        初始化Mock客户端
        :param intent_mapping: 用户输入到意图名称的映射字典
        """
        self.intent_mapping = intent_mapping or {}
        self.call_history = []
```

**使用场景**：
- 测试意图识别功能
- 测试解释器与LLM的集成
- 避免真实API调用（节省成本和时间）

#### 4.2.2 FailingLLMClient

**功能**：
- 模拟LLM API调用失败
- 测试降级机制

**设计说明**：
```python
class FailingLLMClient(LLMClient):
    def identify_intent(self, user_input: str, intents: List) -> Optional[str]:
        raise Exception("LLM API调用失败")
```

**使用场景**：
- 测试LLM失败时的降级处理
- 验证系统健壮性

### 4.3 测试驱动设计

#### 4.3.1 TestDriver

**位置**：`tests/drivers/test_driver.py`

**功能**：
- 统一执行所有测试用例
- 生成测试报告
- 统计测试结果

**设计说明**：
```python
class TestDriver:
    def run_all_tests(self) -> dict:
        """运行所有测试"""
        # 使用pytest运行测试
        # 解析输出
        # 返回结果
    
    def generate_report(self, output_file: str = "test_report.json"):
        """生成测试报告"""
```

**使用方式**：
```bash
python run_tests.py
```

### 4.4 自动测试脚本

#### 4.4.1 run_tests.py

**功能**：
- 一键运行所有测试
- 生成测试报告
- 返回退出码（用于CI/CD）

**脚本内容**：
```python
from tests.drivers.test_driver import TestDriver

def main():
    driver = TestDriver()
    results = driver.run_all_tests()
    driver.generate_report("test_report.json")
    sys.exit(results.get('exit_code', 0))
```

### 4.5 测试用例

#### 4.5.1 词法分析测试

**文件**：`tests/test_lexer.py`

**测试用例**：
- `test_basic_tokens`: 测试基本Token识别
- `test_string_literal`: 测试字符串字面量
- `test_keywords`: 测试关键字识别
- `test_identifier`: 测试标识符识别
- `test_special_characters`: 测试特殊字符
- `test_comments`: 测试注释处理

#### 4.5.2 语法分析测试

**文件**：`tests/test_parser.py`

**测试用例**：
- `test_parse_simple_intent`: 测试简单意图解析
- `test_parse_multiple_patterns`: 测试多模式匹配
- `test_parse_options`: 测试选项解析
- `test_parse_set_action`: 测试Set动作解析
- `test_parse_multiple_intents`: 测试多意图解析

#### 4.5.3 解释器测试

**文件**：`tests/test_interpreter.py`

**测试用例**：
- `test_interpreter_basic`: 测试基本解释功能
- `test_interpreter_variables`: 测试变量管理
- `test_interpreter_template_formatting`: 测试模板格式化

#### 4.5.4 集成测试

**文件**：`tests/test_integration.py`

**测试用例**：
- `test_end_to_end_order_query`: 端到端订单查询测试
- `test_multiple_intents`: 多意图测试

#### 4.5.5 测试桩测试

**文件**：`tests/test_with_stubs.py`

**测试用例**：
- `test_with_mock_llm_client`: 测试Mock LLM客户端
- `test_with_failing_llm_client`: 测试LLM失败降级

### 4.6 测试结果

#### 4.6.1 测试统计

运行命令：`python -m pytest tests/ -v`

**测试结果**：
```
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.0.1
collected 18 items

tests/test_integration.py::test_end_to_end_order_query PASSED
tests/test_integration.py::test_multiple_intents PASSED
tests/test_interpreter.py::test_interpreter_basic PASSED
tests/test_interpreter.py::test_interpreter_variables PASSED
tests/test_interpreter.py::test_interpreter_template_formatting PASSED
tests/test_lexer.py::test_basic_tokens PASSED
tests/test_lexer.py::test_string_literal PASSED
tests/test_lexer.py::test_keywords PASSED
tests/test_lexer.py::test_identifier PASSED
tests/test_lexer.py::test_special_characters PASSED
tests/test_lexer.py::test_comments PASSED
tests/test_parser.py::test_parse_simple_intent PASSED
tests/test_parser.py::test_parse_multiple_patterns PASSED
tests/test_parser.py::test_parse_options PASSED
tests/test_parser.py::test_parse_set_action PASSED
tests/test_parser.py::test_parse_multiple_intents PASSED
tests/test_with_stubs.py::test_with_mock_llm_client PASSED
tests/test_with_stubs.py::test_with_failing_llm_client PASSED

======================== 18 passed in 0.09s ========================
```

**测试覆盖率**：
- 总测试用例数：18
- 通过数：18
- 失败数：0
- 通过率：100%

#### 4.6.2 测试数据

**测试数据文件**：`tests/test_data/`

- `sample_scripts/`: 测试用DSL脚本
- `test_inputs.json`: 测试输入数据

---

## 5. DSL脚本编写指南

### 5.1 文法定义

详见：`docs/dsl_grammar.md`

#### 5.1.1 BNF文法

```
<program> ::= <intent_decl>*

<intent_decl> ::= "intent" <string_literal> "{" <intent_body> "}"

<intent_body> ::= <when_clause> <action>*

<when_clause> ::= "when" "user_says" <string_list> "{"

<string_list> ::= <string_literal> ("or" <string_literal>)*

<action> ::= <ask_action> | <wait_action> | <response_action> | <set_action> | <options_action>

<ask_action> ::= "ask" <string_literal>
<wait_action> ::= "wait_for" <identifier>
<response_action> ::= "response" <string_literal>
<set_action> ::= "set" <identifier> "=" <expression>
<options_action> ::= "options" "[" <string_list> "]"

<expression> ::= <string_literal> | <function_call> | <variable>
<function_call> ::= <identifier> "(" <argument_list> ")"
<variable> ::= "$" <identifier>
```

### 5.2 关键字

- `intent`: 定义意图
- `when`: 条件匹配
- `user_says`: 用户输入模式
- `ask`: 询问用户
- `wait_for`: 等待用户输入
- `response`: 响应
- `set`: 设置变量
- `options`: 提供选项

### 5.3 用法说明

#### 5.3.1 基本结构

```dsl
intent "意图名称" {
    when user_says "模式1" or "模式2" {
        # 动作列表
    }
}
```

#### 5.3.2 动作类型

1. **ask**: 向用户提问
   ```dsl
   ask "请输入您的订单号"
   ```

2. **wait_for**: 等待用户输入并保存到变量
   ```dsl
   wait_for order_number
   ```

3. **response**: 输出响应（支持变量和函数调用）
   ```dsl
   response "您的订单 {order_number} 状态是：{get_order_status(order_number)}"
   ```

4. **set**: 设置变量
   ```dsl
   set refund_id = create_refund(order_number, reason)
   ```

5. **options**: 提供选项
   ```dsl
   options ["选项1", "选项2", "选项3"]
   ```

### 5.4 脚本范例

详见：`scripts/` 目录

- `order_query.dsl`: 订单查询场景
- `refund.dsl`: 退款申请场景
- `tech_support.dsl`: 技术支持场景
- `combined.dsl`: 综合场景

---

## 6. AI辅助开发记录

详见：`docs/ai_development_log.md`

### 6.1 使用的工具

- **工具名称**: Cursor AI Assistant (基于GPT模型)
- **使用时间**: 2025年开发期间
- **主要用途**: 代码生成、架构设计、问题调试

### 6.2 使用过程概述

1. **项目初始化阶段**：AI辅助理解需求、设计项目结构
2. **核心功能实现**：AI辅助实现词法分析器、语法分析器、解释器
3. **LLM集成**：AI辅助设计LLM客户端接口和实现
4. **测试开发**：AI辅助创建测试桩、测试驱动和测试用例
5. **文档编写**：AI辅助整理和编写项目文档

### 6.3 关键对话记录

详见：`docs/ai_development_log.md` 中的详细记录

---

## 7. Git日志

### 7.1 完整Git日志

详见以下文件：
- `docs/git_log_complete.txt` - 完整日志（详细格式）
- `docs/git_log_simple.txt` - 简洁格式
- `docs/git_log_markdown.md` - Markdown格式
- `docs/git_log_table.md` - 表格格式

### 7.2 主要提交记录

1. **Initial commit**: 项目初始化
2. **feat: 实现DSL解释器核心功能**: 添加词法分析器、语法分析器、解释器、LLM客户端和CLI界面
3. **test: 补充测试桩、测试驱动和自动测试脚本**: 修复解析器bug，所有测试通过
4. **Improve intent matching**: 优化意图匹配逻辑，改进LLM回退机制和简单匹配算法

### 7.3 版本管理说明

- 所有提交都有完整的注释
- 使用语义化提交信息
- 每个版本都有明确的功能说明

---

## 附录

### A. 项目文件结构

```
DSL/
├── src/                    # 源代码
│   ├── lexer.py           # 词法分析器
│   ├── parser.py          # 语法分析器
│   ├── interpreter.py     # 解释器
│   ├── llm_client.py      # LLM客户端
│   └── cli.py             # 命令行界面
├── scripts/               # DSL脚本范例
│   ├── order_query.dsl    # 订单查询
│   ├── refund.dsl         # 退款申请
│   ├── tech_support.dsl   # 技术支持
│   └── combined.dsl       # 综合场景
├── tests/                 # 测试代码
│   ├── stubs/             # 测试桩
│   ├── drivers/           # 测试驱动
│   ├── test_data/         # 测试数据
│   └── test_*.py          # 测试用例
├── docs/                  # 文档
│   ├── dsl_grammar.md     # DSL语法定义
│   ├── ai_development_log.md  # AI开发记录
│   └── git_log_*.txt/md   # Git日志
├── run_tests.py           # 自动测试脚本
├── requirements.txt       # 依赖管理
└── README.md              # 项目说明
```

### B. 依赖列表

详见：`requirements.txt`

- openai>=1.0.0
- pytest>=7.0.0
- pytest-cov>=4.0.0
- python-dotenv>=1.0.0
- requests>=2.31.0

---

**文档结束**

