# 简单的退款脚本（用于测试）
intent "退款申请" {
    when user_says "退款" {
        ask "请输入订单号"
        wait_for order_number
        response "退款申请已提交"
    }
}

