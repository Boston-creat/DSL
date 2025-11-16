# 售后服务中心脚本 - 展示完整的售后流程

# 售后服务咨询
intent "售后服务咨询" {
    when user_says "售后" or "售后服务" or "售后咨询" or "需要售后" or "售后问题" {
        ask "请选择您需要的售后服务类型"
        options ["换货", "维修", "退货", "其他"]
        wait_for service_type
        set service_info = get_after_sales_service(service_type)
        response "{service_info}\n\n需要我帮您申请{service_type}服务吗？"
    }
}

# 换货申请
intent "换货申请" {
    when user_says "换货" or "申请换货" or "我要换货" or "换货服务" {
        ask "请输入您的订单号"
        wait_for order_number
        ask "请选择换货原因"
        options ["质量问题", "尺寸不合适", "颜色不喜欢", "发错货", "其他"]
        wait_for reason
        ask "请描述您要换的商品信息（型号、规格等）"
        wait_for new_product_info
        set ticket_id = create_ticket("换货申请")
        response "换货申请已提交！\n\n申请编号：{ticket_id}\n订单号：{order_number}\n换货原因：{reason}\n新商品信息：{new_product_info}\n\n我们将在24小时内审核您的换货申请，审核通过后安排免费上门取件。\n\n您可以通过申请编号随时查询换货进度！"
    }
}

# 维修申请
intent "维修申请" {
    when user_says "维修" or "申请维修" or "我要维修" or "维修服务" or "商品坏了" {
        ask "请输入您的订单号"
        wait_for order_number
        ask "请描述商品故障情况（越详细越好）"
        wait_for problem_description
        ask "请选择维修方式"
        options ["上门维修", "寄回维修", "到店维修"]
        wait_for repair_method
        set ticket_id = create_ticket("维修申请")
        response "维修申请已提交！\n\n申请编号：{ticket_id}\n订单号：{order_number}\n故障描述：{problem_description}\n维修方式：{repair_method}\n\n我们的维修团队将在24小时内联系您，安排维修事宜。\n\n在保修期内的商品享受免费维修服务！"
    }
}

# 退货申请
intent "退货申请" {
    when user_says "退货" or "申请退货" or "我要退货" or "退货服务" {
        ask "请输入您的订单号"
        wait_for order_number
        ask "请选择退货原因"
        options ["质量问题", "不想要了", "发错货", "买错了", "其他"]
        wait_for reason
        ask "商品是否已使用？"
        options ["未使用", "已使用但完好", "已损坏"]
        wait_for product_condition
        set refund_id = create_refund(order_number, reason)
        response "退货申请已提交！\n\n申请编号：{refund_id}\n订单号：{order_number}\n退货原因：{reason}\n商品状态：{product_condition}\n\n我们将在24小时内审核您的退货申请。\n\n7天无理由退货：商品未使用可全额退款，运费由我们承担！\n\n您可以通过申请编号随时查询退货进度！"
    }
}

# 售后进度查询
intent "售后进度查询" {
    when user_says "售后进度" or "查询进度" or "进度查询" or "处理进度" or "售后状态" {
        ask "请输入您的售后申请编号"
        wait_for ticket_id
        set refund_status = get_refund_status()
        response "售后申请进度：{refund_status}\n\n申请编号：{ticket_id}\n当前状态：处理中\n预计完成时间：3-5个工作日\n\n我们会及时更新处理进度，您也可以通过申请编号随时查询！"
    }
}

# 质保查询
intent "质保查询" {
    when user_says "质保" or "保修" or "质保期" or "保修期" or "质保查询" {
        ask "请输入您的订单号"
        wait_for order_number
        response "质保信息查询：\n\n订单号：{order_number}\n质保期限：1年\n质保范围：\n✅ 商品质量问题\n✅ 非人为损坏\n✅ 正常使用故障\n\n质保服务：\n🔧 免费维修\n🔄 免费换货\n📦 免费上门取件\n\n质保期内享受免费售后服务，超出质保期可提供付费维修服务。\n\n您需要申请质保服务吗？"
    }
}

# 售后政策咨询
intent "售后政策咨询" {
    when user_says "售后政策" or "政策" or "售后规则" or "退换货政策" or "售后规定" {
        response "售后服务政策：\n\n📋 退换货政策：\n• 7天无理由退货\n• 15天质量问题换货\n• 1年免费质保\n\n💰 退款说明：\n• 退款3-5个工作日到账\n• 运费由我们承担\n• 支持原路退回\n\n🔧 维修服务：\n• 质保期内免费维修\n• 全国联保服务\n• 提供备用机服务\n\n📦 物流服务：\n• 免费上门取件\n• 免费寄回服务\n• 全程物流跟踪\n\n您想了解哪个政策的详细信息？"
    }
}

