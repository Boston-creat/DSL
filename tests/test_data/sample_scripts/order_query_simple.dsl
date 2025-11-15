# 简单的订单查询脚本（用于测试）
intent "订单查询" {
    when user_says "查询订单" {
        ask "请输入订单号"
        wait_for order_number
        response "订单 {order_number} 状态：已发货"
    }
}

