# 会员服务中心脚本 - 展示会员等级、积分系统

# 会员信息查询
intent "会员信息查询" {
    when user_says "会员" or "我的会员" or "会员信息" or "查会员" or "会员等级" or "会员状态" {
        ask "请输入您的会员ID或手机号"
        wait_for member_id
        set account_status = check_account_status(member_id)
        response "{account_status}\n\n您想了解会员权益、积分情况还是升级信息？"
    }
}

# 会员权益查询
intent "会员权益查询" {
    when user_says "会员权益" or "权益" or "会员特权" or "有什么权益" or "权益查询" {
        ask "请输入您的会员ID"
        wait_for member_id
        set benefits = get_member_benefits(member_id)
        response "{benefits}\n\n会员权益包括：\n✅ 积分兑换\n✅ 等级提升\n✅ 专属优惠\n✅ 专属客服\n✅ 生日特权\n✅ 免费退换货\n\n您想了解哪个权益的详细信息？"
    }
}

# 积分查询
intent "积分查询" {
    when user_says "积分" or "我的积分" or "积分多少" or "查积分" or "积分余额" or "积分查询" {
        ask "请输入您的会员ID"
        wait_for member_id
        response "您的当前积分：1,250分\n\n积分获取方式：\n💰 购物消费：每消费1元获得1积分\n🎁 签到奖励：每日签到获得10积分\n🎉 活动奖励：参与活动可获得额外积分\n\n积分用途：\n🛒 积分兑换：100积分=1元，可抵扣订单金额\n🎁 积分商城：使用积分兑换精美礼品\n\n您想使用积分吗？或者了解积分兑换规则？"
    }
}

# 会员升级
intent "会员升级" {
    when user_says "升级" or "会员升级" or "升级会员" or "如何升级" or "升级条件" {
        response "会员升级规则：\n\n📊 等级体系：\n• 普通会员：注册即可\n• 银卡会员：累计消费满500元\n• 金卡会员：累计消费满2000元\n• 钻石会员：累计消费满5000元\n• VIP会员：累计消费满10000元\n\n🎁 升级奖励：\n• 升级即可获得积分奖励\n• 享受更高折扣优惠\n• 专属客服优先处理\n• 生日月额外福利\n\n您当前是金卡会员，再消费¥750即可升级为钻石会员！\n\n需要我帮您查看升级进度吗？"
    }
}

# 积分兑换
intent "积分兑换" {
    when user_says "积分兑换" or "兑换" or "用积分" or "积分换" or "兑换商品" {
        ask "请输入您要兑换的商品名称或编号"
        wait_for product_name
        response "积分兑换商品：{product_name}\n\n所需积分：500分\n您的可用积分：1,250分\n\n兑换后剩余积分：750分\n\n确认兑换吗？兑换成功后商品将直接加入您的购物车！"
    }
}

# 生日特权
intent "生日特权" {
    when user_says "生日" or "生日特权" or "生日优惠" or "生日礼物" or "生日福利" {
        response "🎂 生日特权活动：\n\n🎁 生日月专属优惠：\n• 生日月购物享受8.5折优惠\n• 生日当天购物额外赠送100积分\n• 生日月专属优惠券：满200减50\n\n🎉 生日惊喜：\n• 生日当天登录即可领取生日大礼包\n• 包含：50元优惠券 + 200积分 + 专属生日徽章\n\n📅 活动时间：生日当月整月有效\n\n您想领取生日特权吗？请提供您的生日信息！"
    }
}

# 会员专享优惠
intent "会员专享优惠" {
    when user_says "会员优惠" or "专享优惠" or "会员折扣" or "会员价" or "会员专享" {
        set promotion = get_promotion_info("会员")
        response "{promotion}\n\n会员专享优惠详情：\n\n👑 VIP会员：\n• 全场8.5折\n• 积分翻倍\n• 专属客服\n\n⭐ 金卡会员：\n• 全场9折\n• 积分1.5倍\n• 优先处理\n\n💎 钻石会员：\n• 全场8.8折\n• 积分1.8倍\n• 专属优惠券\n\n您想了解如何成为VIP会员吗？"
    }
}

