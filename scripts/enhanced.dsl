# 增强版综合场景脚本 - 包含丰富的业务场景和幽默对话

# 订单查询（增强版，带幽默和追问）
intent "订单查询" {
    when user_says "查询订单" or "我的订单" or "订单状态" or "查看订单" or "订单查询" or "查订单" or "订单" or "我想查订单" or "订单在哪里" or "查一下订单" or "订单详情" or "订单信息" {
        ask "请输入您的订单号（如果没有订单号，输入'没有'我可以帮您找找）"
        wait_for order_number
        set order_status = get_order_status(order_number)
        response "好的，让我看看...（假装在查找🔍）您的订单 {order_number} 状态是：{order_status}。虽然我是机器人，但我很聪明的😎\n\n{get_follow_up_question(订单)}"
    }
}

# 订单追问（深度对话）
intent "订单追问" {
    when user_says "物流" or "配送" or "什么时候到" or "送达时间" or "物流详情" or "配送方式" or "快递" or "运输" or "订单物流" {
        response "关于物流信息：您的订单预计3-5个工作日送达。您可以通过订单号在物流查询页面查看实时物流轨迹。{get_related_topic(订单)}"
    }
}

# 退款申请（增强版，带更多选项和幽默）
intent "退款申请" {
    when user_says "退款" or "退货" or "申请退款" or "我要退款" or "退钱" or "不想要了" or "想退货" {
        ask "这个问题有点意思，让我来帮您解决！请选择退款原因（这很重要哦，关系到退款速度）"
        options ["质量问题", "不想要了", "发错货", "买错了", "其他原因"]
        wait_for reason
        ask "请输入订单号（别担心，退款很快的😄）"
        wait_for order_number
        set refund_id = create_refund(order_number, reason)
        response "退款申请已提交！申请号：{refund_id}，预计3-5个工作日处理（我们会尽快，比您想象的快！）\n\n{get_follow_up_question(退款)}"
    }
}

# 退款追问（深度对话）
intent "退款追问" {
    when user_says "退款进度" or "退款到账" or "什么时候到账" or "退款方式" or "退款状态" or "退款查询" or "退款多久" {
        response "关于退款进度：退款通常在3-5个工作日内到账，具体到账时间取决于您的支付方式。您可以通过退款申请号随时查询进度。{get_related_topic(退款)}"
    }
}

# 技术支持（增强版，带分类和幽默）
intent "技术支持" {
    when user_says "故障" or "问题" or "无法使用" or "需要帮助" or "技术支持" or "出问题了" or "系统故障" or "用不了" {
        ask "让我想想...（假装思考中🤔）请先选择问题类型，这样我能更快帮到您"
        options ["登录问题", "支付问题", "功能异常", "其他问题"]
        wait_for problem_type
        ask "请详细描述您遇到的问题（越详细越好，就像写作文一样📝）"
        wait_for problem_description
        set ticket_id = create_ticket(problem_description)
        response "已为您创建工单 {ticket_id}！我们的技术支持团队将在24小时内联系您（他们比我还聪明，一定能解决您的问题！）收到！正在处理中..."
    }
}

# 优惠券查询（新场景，带幽默）
intent "优惠券查询" {
    when user_says "优惠券" or "券" or "优惠" or "折扣券" or "领取优惠券" or "有优惠吗" or "优惠活动" {
        ask "好的，我明白了！虽然我是机器人，但我很聪明的😎 请选择您想要的优惠券类型（选对了有惊喜哦🎁）"
        options ["新用户", "生日", "节日", "随便来一个"]
        wait_for coupon_type
        set coupon = get_coupon(coupon_type)
        response "恭喜您！{coupon} 优惠券已发放到您的账户，快去使用吧！（手慢无哦😉）\n\n{get_follow_up_question(优惠)}"
    }
}

# 优惠追问（深度对话）
intent "优惠追问" {
    when user_says "更多优惠" or "其他优惠" or "限时活动" or "会员折扣" or "满减" or "生日特权" or "还有什么优惠" {
        response "关于更多优惠：我们还有限时活动、会员专享折扣、满减优惠、生日特权等多种优惠方式。{get_related_topic(优惠)}"
    }
}

# 商品推荐（新场景，带幽默和个性化）
intent "商品推荐" {
    when user_says "推荐" or "推荐商品" or "有什么好商品" or "买什么" or "推荐一下" or "有什么推荐" {
        ask "请告诉我您想买什么类型的商品（比如：手机、电脑、耳机等，或者随便看看）"
        wait_for product_keyword
        set recommendation = recommend_product(product_keyword)
        response "{recommendation}\n\n{get_follow_up_question(商品)}"
    }
}

# 商品追问（深度对话）
intent "商品追问" {
    when user_says "规格" or "参数" or "评价" or "评论" or "使用说明" or "保修" or "详情" or "详细介绍" or "商品详情" {
        response "关于商品详情：我们提供详细的商品规格、用户评价、使用说明和保修政策。您可以在商品详情页查看完整信息。{get_related_topic(商品)}"
    }
}

# 账户查询（新场景，带幽默）
intent "账户查询" {
    when user_says "账户" or "我的账户" or "账户状态" or "查账户" or "账户信息" or "会员" {
        ask "收到！正在处理中...请输入您的账户名或手机号（放心，我不会泄露的，我可是很专业的🔒）"
        wait_for account
        set account_status = check_account_status(account)
        response "{account_status} 这个问题有点意思，让我来帮您解决！\n\n{get_follow_up_question(账户)}"
    }
}

# 账户追问（深度对话）
intent "账户追问" {
    when user_says "会员权益" or "积分" or "积分查询" or "等级" or "升级" or "专属优惠" or "会员特权" {
        response "关于会员权益：我们的会员可以享受积分兑换、等级提升、专属优惠、专属客服等多种特权。{get_related_topic(账户)}"
    }
}

# 投诉建议（新场景，带幽默和分类）
intent "投诉建议" {
    when user_says "投诉" or "建议" or "意见" or "不满意" or "有问题" or "要投诉" or "提建议" {
        ask "让我想想...（假装思考中🤔）请选择类型（我们会认真对待每一条反馈的）"
        options ["服务投诉", "产品建议", "功能建议", "其他反馈"]
        wait_for feedback_type
        ask "请详细描述您的投诉或建议（我们会认真阅读的，就像读情书一样认真💌）"
        wait_for feedback_content
        set feedback_id = create_ticket(feedback_content)
        response "感谢您的反馈！反馈编号：{feedback_id}。我们会认真处理您的意见，让服务变得更好！（您的建议比咖啡还提神☕）好的，我明白了！虽然我是机器人，但我很聪明的😎"
    }
}

# 价格计算（新场景，带幽默）
intent "价格计算" {
    when user_says "计算价格" or "算价格" or "多少钱" or "价格" or "折扣" or "优惠多少" {
        ask "请输入商品原价（数字就行，比如：100）"
        wait_for price
        ask "请选择折扣类型（选对了能省不少钱呢💰）"
        options ["新用户", "VIP", "节日", "默认"]
        wait_for discount_type
        set discount_info = calculate_discount(price, discount_type)
        response "{discount_info}"
    }
}

# 问候闲聊（新场景，带幽默）
intent "问候闲聊" {
    when user_says "你好" or "hello" or "hi" or "在吗" or "有人吗" or "客服" {
        response "您好！我是智能客服小助手，24小时在线为您服务！有什么可以帮您的吗？"
    }
}

# 感谢告别（新场景，带幽默）
intent "感谢告别" {
    when user_says "谢谢" or "感谢" or "再见" or "拜拜" or "88" or "thank you" {
        response "收到！正在处理中...不客气！很高兴能帮助到您！如果还有其他问题，随时来找我哦！（我会一直在这里等您的😊）祝您生活愉快！"
    }
}

# 通用追问（深度对话 - 支持继续追问）
intent "通用追问" {
    when user_says "继续" or "还有吗" or "详细说明" or "多说点" or "再详细点" or "还有呢" or "然后呢" or "接着说" or "继续讲" or "详细点" or "更多信息" {
        set follow_up = get_follow_up_question(last_intent)
        response "好的，让我继续为您介绍。{follow_up} 或者您也可以直接问我具体的问题，我会详细解答的！"
    }
}

# 话题发散（深度对话 - 支持话题扩展）
intent "话题发散" {
    when user_says "还有什么" or "其他服务" or "还能做什么" or "还有什么功能" or "其他" or "还有别的吗" or "还有什么可以问" or "相关服务" {
        set related = get_related_topic(last_intent)
        response "当然有！{related} 您想了解哪个呢？"
    }
}

