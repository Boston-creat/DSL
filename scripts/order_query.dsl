# 订单查询场景脚本
intent "订单查询" {
    when user_says "查询订单" or "我的订单" or "订单状态" or "查看订单" {
        ask "请输入您的订单号"
        wait_for order_number
        response "您的订单 {order_number} 状态是：{get_order_status(order_number)}"
    }
}

