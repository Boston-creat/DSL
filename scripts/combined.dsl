# 综合场景脚本 - 包含多个业务场景

# 订单查询
intent "订单查询" {
    when user_says "查询订单" or "我的订单" or "订单状态" or "查看订单" or "订单查询" or "查订单" or "订单" {
        ask "请输入您的订单号"
        wait_for order_number
        response "您的订单 {order_number} 状态是：{get_order_status(order_number)}"
    }
}

# 退款申请
intent "退款申请" {
    when user_says "退款" or "退货" or "申请退款" or "我要退款" {
        ask "请选择退款原因"
        options ["质量问题", "不想要了", "发错货", "其他"]
        wait_for reason
        ask "请输入订单号"
        wait_for order_number
        set refund_id = create_refund(order_number, reason)
        response "退款申请已提交，申请号：{refund_id}，预计3-5个工作日处理"
    }
}

# 技术支持
intent "技术支持" {
    when user_says "故障" or "问题" or "无法使用" or "需要帮助" or "技术支持" {
        ask "请描述您遇到的问题"
        wait_for problem_description
        set ticket_id = create_ticket(problem_description)
        response "已为您创建工单 {ticket_id}，我们的技术支持团队将在24小时内联系您"
    }
}

