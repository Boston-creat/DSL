# 智能购物助手脚本 - 展示个性化推荐和购物流程

# 个性化商品推荐
intent "个性化推荐" {
    when user_says "推荐" or "推荐商品" or "有什么推荐" or "给我推荐" or "推荐一下" or "个性化推荐" or "智能推荐" {
        ask "请告诉我您的用户ID或手机号（用于个性化推荐）"
        wait_for user_id
        set preferences = get_user_preferences(user_id)
        response "根据您的偏好分析：{preferences}\n\n请告诉我您想买什么类型的商品（比如：手机、电脑、耳机等）"
        wait_for product_category
        set recommendation = get_personalized_recommendation(user_id, product_category)
        response "{recommendation}\n\n您还想了解商品的库存情况、价格优惠或其他信息吗？"
    }
}

# 库存查询
intent "库存查询" {
    when user_says "库存" or "有货吗" or "还有吗" or "库存多少" or "查库存" or "库存查询" {
        ask "请输入您要查询的商品名称"
        wait_for product_name
        set inventory_info = check_inventory(product_name)
        response "{inventory_info}\n\n需要我帮您下单吗？或者您还想了解其他信息？"
    }
}

# 运费计算
intent "运费计算" {
    when user_says "运费" or "邮费" or "快递费" or "计算运费" or "运费多少" or "包邮吗" {
        ask "请输入收货地址（比如：北京市朝阳区）"
        wait_for address
        ask "请输入商品重量（单位：kg，比如：1.5）"
        wait_for weight
        set shipping_fee = calculate_shipping_fee(address, weight)
        response "{shipping_fee}\n\n满99元包邮，您当前订单可以享受包邮服务！"
    }
}

# 促销活动查询
intent "促销查询" {
    when user_says "促销" or "活动" or "优惠活动" or "有什么活动" or "限时活动" or "促销信息" {
        ask "请选择您想了解的活动类型"
        options ["限时", "节日", "会员"]
        wait_for promotion_type
        set promotion_info = get_promotion_info(promotion_type)
        response "{promotion_info}\n\n更多活动详情请查看活动页面，或咨询客服了解详情！"
    }
}

# 价格查询
intent "价格查询" {
    when user_says "价格" or "多少钱" or "价格多少" or "查价格" or "价格查询" {
        ask "请输入商品原价（数字，比如：1000）"
        wait_for original_price
        ask "请选择折扣类型"
        options ["新用户", "VIP", "节日", "默认"]
        wait_for discount_type
        set discount_info = calculate_discount(original_price, discount_type)
        set formatted_price = format_price(original_price)
        response "商品原价：{formatted_price}\n{discount_info}\n\n需要我帮您下单吗？"
    }
}

# 购物车咨询
intent "购物车咨询" {
    when user_says "购物车" or "我的购物车" or "购物车有什么" or "查看购物车" {
        response "您的购物车中有3件商品，总价：¥1,299.00\n\n1. 智能手机 - ¥899.00\n2. 蓝牙耳机 - ¥299.00\n3. 手机壳 - ¥101.00\n\n满1000元可享受9折优惠，当前可优惠¥129.90！\n\n需要我帮您结算吗？或者您想了解其他信息？"
    }
}

# 订单跟踪
intent "订单跟踪" {
    when user_says "跟踪订单" or "订单跟踪" or "物流跟踪" or "查物流" or "订单在哪" {
        ask "请输入您的订单号"
        wait_for order_number
        set logistics = get_logistics_info()
        response "订单 {order_number} 物流信息：{logistics}\n\n您可以通过订单号在物流查询页面查看实时物流轨迹。\n\n预计3-5个工作日送达，请耐心等待！"
    }
}

