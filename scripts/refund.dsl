# 退款申请场景脚本
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

