# DSL 语法定义

## 语法概述

本DSL用于描述智能客服机器人的应答逻辑，支持意图识别、条件判断、用户交互和响应生成。

## BNF 文法定义

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

<argument_list> ::= <expression> ("," <expression>)*

<variable> ::= "$" <identifier>

<identifier> ::= [a-zA-Z_][a-zA-Z0-9_]*

<string_literal> ::= "\"" <string_content> "\""

<string_content> ::= (任意字符，支持转义)
```

## 关键字

- `intent`: 定义意图
- `when`: 条件匹配
- `user_says`: 用户输入匹配
- `ask`: 询问用户
- `wait_for`: 等待用户输入
- `response`: 生成响应
- `set`: 设置变量
- `options`: 提供选项列表
- `or`: 逻辑或

## 示例脚本

### 示例1：订单查询

```
intent "订单查询" {
    when user_says "查询订单" or "我的订单" or "订单状态" {
        ask "请输入您的订单号"
        wait_for order_number
        response "您的订单 {order_number} 状态是：{get_order_status(order_number)}"
    }
}
```

### 示例2：退款申请

```
intent "退款申请" {
    when user_says "退款" or "退货" or "申请退款" {
        ask "请选择退款原因"
        options ["质量问题", "不想要了", "发错货", "其他"]
        wait_for reason
        set refund_id = create_refund(order_number, reason)
        response "退款申请已提交，申请号：{refund_id}，预计3-5个工作日处理"
    }
}
```

### 示例3：技术支持

```
intent "技术支持" {
    when user_says "故障" or "问题" or "无法使用" {
        ask "请描述您遇到的问题"
        wait_for problem_description
        set ticket_id = create_ticket(problem_description)
        response "已为您创建工单 {ticket_id}，我们的技术支持团队将在24小时内联系您"
    }
}
```

