"""
解释器（Interpreter）
作用：遍历AST并执行相应的动作，实现DSL脚本的运行时行为
在全项目中的作用：这是编译过程的第三步，将AST转换为实际的执行逻辑，处理用户交互、变量管理和函数调用
"""

from typing import Dict, Any, Callable, Optional, List
from src.parser import (
    Program, IntentDecl, WhenClause, Action, AskAction, WaitForAction,
    ResponseAction, SetAction, OptionsAction, Expression, StringLiteral,
    Variable, FunctionCall
)


class Interpreter:
    """解释器"""
    
    def __init__(self, llm_client=None):
        """
        初始化解释器
        :param llm_client: LLM客户端实例，用于意图识别
        """
        self.llm_client = llm_client
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Callable] = {
            'get_order_status': self._get_order_status,
            'create_refund': self._create_refund,
            'create_ticket': self._create_ticket,
            'get_coupon': self._get_coupon,
            'recommend_product': self._recommend_product,
            'check_account_status': self._check_account_status,
            'get_humor_response': self._get_humor_response,
            'calculate_discount': self._calculate_discount,
            'get_follow_up_question': self._get_follow_up_question,
            'get_related_topic': self._get_related_topic,
            'get_logistics_info': self._get_logistics_info,
            'get_refund_status': self._get_refund_status,
            'get_more_coupons': self._get_more_coupons,
            'get_product_details': self._get_product_details,
            'get_member_benefits': self._get_member_benefits,
            'get_personalized_recommendation': self._get_personalized_recommendation,
            'calculate_shipping_fee': self._calculate_shipping_fee,
            'get_promotion_info': self._get_promotion_info,
            'check_inventory': self._check_inventory,
            'get_after_sales_service': self._get_after_sales_service,
            'get_user_preferences': self._get_user_preferences,
            'format_price': self._format_price,
        }
        self.current_intent: Optional[IntentDecl] = None
        self.user_input_callback: Optional[Callable[[str], str]] = None
        self.output_callback: Optional[Callable[[str], None]] = None  # 输出回调（用于GUI）
        # 对话历史记录
        self.conversation_history: List[Dict[str, str]] = []  # [{"role": "user"/"bot", "content": "..."}]
        self.last_intent: Optional[str] = None  # 上一次的意图
        self.last_context: Dict[str, Any] = {}  # 上一次的上下文信息
    
    def set_user_input_callback(self, callback: Callable[[str], str]):
        """设置用户输入回调函数"""
        self.user_input_callback = callback
    
    def set_output_callback(self, callback: Callable[[str], None]):
        """设置输出回调函数（用于GUI等非CLI界面）"""
        self.output_callback = callback
    
    def _output(self, message: str):
        """输出消息（优先使用回调，否则使用print）"""
        if self.output_callback:
            self.output_callback(message)
        else:
            print(message)
    
    def interpret(self, program: Program) -> Dict[str, Any]:
        """
        解释执行程序
        :param program: 程序AST
        :return: 执行结果
        """
        self.variables.clear()
        result = {
            'matched_intent': None,
            'response': None,
            'variables': {}
        }
        
        # 存储所有意图，供意图识别使用
        self.intents = program.intents
        
        return result
    
    def match_intent(self, user_input: str) -> Optional[IntentDecl]:
        """
        匹配用户输入的意图（支持对话历史和上下文）
        :param user_input: 用户输入
        :return: 匹配的意图，如果没有匹配则返回None
        :raises RuntimeError: 如果LLM客户端未配置
        """
        # 检查intents是否已设置
        if not hasattr(self, 'intents') or not self.intents:
            return None
        
        # 必须使用LLM客户端进行意图识别
        if not self.llm_client:
            raise RuntimeError(
                "LLM客户端未配置。本项目要求使用API进行意图识别。\n"
                "请配置 ZHIPUAI_API_KEY 环境变量。"
            )
        
        # 记录用户输入到对话历史
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # 使用LLM进行意图识别（带对话历史）
        try:
            intent_name = self.llm_client.identify_intent(
                user_input, 
                self.intents,
                conversation_history=self.conversation_history[-5:] if len(self.conversation_history) > 1 else [],  # 只传递最近5轮对话
                last_intent=self.last_intent,
                last_context=self.last_context
            )
            if intent_name:
                for intent in self.intents:
                    if intent.name == intent_name:
                        return intent
            return None
        except Exception as e:
            # LLM失败时抛出异常，不再fallback
            raise RuntimeError(f"意图识别失败: {e}")
    
    def execute_intent(self, intent: IntentDecl) -> Dict[str, Any]:
        """
        执行意图（记录对话历史）
        :param intent: 意图声明
        :return: 执行结果
        """
        self.current_intent = intent
        # 保留上一次的变量（用于上下文）
        if not self.last_context:
            self.variables.clear()
        else:
            # 保留关键变量
            for key in ['order_number', 'reason', 'problem_description', 'account', 'product_keyword']:
                if key in self.last_context:
                    self.variables[key] = self.last_context[key]
        
        result = {
            'response': None,
            'variables': {}
        }
        
        # 执行所有动作
        for action in intent.actions:
            action_result = self.execute_action(action)
            if action_result and 'response' in action_result:
                result['response'] = action_result['response']
            if action_result and 'variables' in action_result:
                result['variables'].update(action_result['variables'])
        
        # 记录对话历史和上下文
        if result.get('response'):
            self.conversation_history.append({"role": "bot", "content": result['response']})
        self.last_intent = intent.name
        self.last_context = self.variables.copy()
        
        return result
    
    def execute_action(self, action: Action) -> Optional[Dict[str, Any]]:
        """执行动作"""
        if isinstance(action, AskAction):
            return self.execute_ask(action)
        elif isinstance(action, WaitForAction):
            return self.execute_wait_for(action)
        elif isinstance(action, ResponseAction):
            return self.execute_response(action)
        elif isinstance(action, SetAction):
            return self.execute_set(action)
        elif isinstance(action, OptionsAction):
            return self.execute_options(action)
        return None
    
    def execute_ask(self, action: AskAction) -> Dict[str, Any]:
        """执行Ask动作"""
        self._output(f"[机器人] {action.message}")
        return {}
    
    def execute_wait_for(self, action: WaitForAction) -> Dict[str, Any]:
        """执行WaitFor动作"""
        if self.user_input_callback:
            user_input = self.user_input_callback(action.variable)
            self.variables[action.variable] = user_input
            return {'variables': {action.variable: user_input}}
        else:
            # 如果没有回调，使用标准输入
            user_input = input(f"请输入 {action.variable}: ")
            self.variables[action.variable] = user_input
            return {'variables': {action.variable: user_input}}
    
    def execute_response(self, action: ResponseAction) -> Dict[str, Any]:
        """执行Response动作"""
        response = self._format_template(action.template)
        self._output(f"[机器人] {response}")
        return {'response': response}
    
    def execute_set(self, action: SetAction) -> Dict[str, Any]:
        """执行Set动作"""
        value = self.evaluate_expression(action.expression)
        self.variables[action.variable] = value
        return {'variables': {action.variable: value}}
    
    def execute_options(self, action: OptionsAction) -> Dict[str, Any]:
        """执行Options动作"""
        options_text = "请选择：\n"
        for i, option in enumerate(action.options, 1):
            options_text += f"  {i}. {option}\n"
        self._output(options_text)
        return {}
    
    def evaluate_expression(self, expr: Expression) -> Any:
        """求值表达式"""
        if isinstance(expr, StringLiteral):
            return expr.value
        elif isinstance(expr, Variable):
            return self.variables.get(expr.name, f"${expr.name}")
        elif isinstance(expr, FunctionCall):
            return self.evaluate_function_call(expr)
        else:
            return str(expr)
    
    def evaluate_function_call(self, call: FunctionCall) -> Any:
        """求值函数调用"""
        func = self.functions.get(call.name)
        if not func:
            # 如果函数不存在，返回一个模拟值
            return f"{call.name}({', '.join(str(self.evaluate_expression(arg)) for arg in call.args)})"
        
        args = [self.evaluate_expression(arg) for arg in call.args]
        return func(*args)
    
    def _format_template(self, template: str) -> str:
        """格式化模板字符串，替换变量和表达式"""
        import re
        
        def replace_expr(match):
            """替换匹配的表达式"""
            expr_str = match.group(1)  # 获取 { } 中的内容
            
            # 首先尝试作为变量名
            if expr_str in self.variables:
                return str(self.variables[expr_str])
            
            # 特殊变量：last_intent
            if expr_str == "last_intent" and hasattr(self, 'last_intent'):
                return str(self.last_intent or "默认")
            
            # 如果不是变量，尝试解析为表达式（函数调用等）
            try:
                # 尝试解析为函数调用，例如 get_order_status(order_number)
                # 简单的函数调用解析
                if '(' in expr_str and ')' in expr_str:
                    func_match = re.match(r'(\w+)\s*\((.*)\)', expr_str)
                    if func_match:
                        func_name = func_match.group(1)
                        args_str = func_match.group(2).strip()
                        
                        # 解析参数
                        args = []
                        if args_str:
                            # 简单的参数解析（支持变量名和特殊变量）
                            for arg in args_str.split(','):
                                arg = arg.strip()
                                # 移除引号（如果是字符串字面量）
                                if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                                    args.append(arg[1:-1])
                                # 如果是变量，获取变量值
                                elif arg in self.variables:
                                    args.append(self.variables[arg])
                                # 特殊变量：last_intent
                                elif arg == "last_intent" and hasattr(self, 'last_intent'):
                                    args.append(self.last_intent or "默认")
                                else:
                                    # 否则作为字符串字面量
                                    args.append(arg)
                        
                        # 调用函数
                        if func_name in self.functions:
                            result = self.functions[func_name](*args)
                            return str(result)
                
                # 如果无法解析，返回原始表达式
                return match.group(0)
            except Exception as e:
                # 如果解析失败，返回原始表达式
                return match.group(0)
        
        # 使用正则表达式找到所有 {expression} 并替换
        pattern = r'\{([^}]+)\}'
        result = re.sub(pattern, replace_expr, template)
        return result
    
    # 内置函数实现
    def _get_order_status(self, order_number: str) -> str:
        """获取订单状态（模拟）"""
        # 实际应用中，这里应该调用真实的API或数据库
        # 根据订单号模拟不同的订单状态
        if not order_number:
            return "订单号无效"
        
        # 根据订单号的最后一位数字模拟不同状态
        try:
            last_digit = int(order_number[-1]) if order_number[-1].isdigit() else 0
            statuses = [
                "待付款",
                "已付款",
                "已发货",
                "运输中",
                "已送达",
                "已完成",
                "已取消",
                "退款中",
                "已退款",
                "待评价"
            ]
            return statuses[last_digit % len(statuses)]
        except:
            # 如果无法解析，默认返回已发货
            return "已发货"
    
    def _create_refund(self, order_number: str, reason: str) -> str:
        """创建退款申请（模拟）"""
        # 实际应用中，这里应该调用真实的API
        refund_id = f"REF{order_number[-4:]}{len(reason)}"
        return refund_id
    
    def _create_ticket(self, description: str) -> str:
        """创建工单（模拟）"""
        # 实际应用中，这里应该调用真实的API
        ticket_id = f"TICKET{hash(description) % 10000:04d}"
        return ticket_id
    
    def _get_coupon(self, category: str) -> str:
        """获取优惠券（模拟，带幽默）"""
        coupons = {
            "新用户": "NEW100（新用户专享100元优惠券，限时3天！）",
            "生日": "BIRTHDAY50（生日快乐！50元优惠券已到账🎂）",
            "节日": "FESTIVAL200（节日特惠200元券，祝您节日快乐！）",
            "默认": "WELCOME20（欢迎使用！20元优惠券送给您）"
        }
        return coupons.get(category, coupons["默认"])
    
    def _recommend_product(self, keyword: str) -> str:
        """推荐商品（模拟，带幽默）"""
        recommendations = {
            "手机": "推荐：最新款智能手机，性能强劲，拍照清晰，价格美丽！📱",
            "电脑": "推荐：高性能笔记本电脑，办公游戏两不误，性价比之王！💻",
            "耳机": "推荐：降噪蓝牙耳机，音质超棒，戴上它世界都是你的！🎧",
            "默认": "推荐：精选好物，品质保证，总有一款适合您！✨"
        }
        # 简单的关键词匹配
        for key, value in recommendations.items():
            if key in keyword:
                return value
        return recommendations["默认"]
    
    def _check_account_status(self, account: str) -> str:
        """检查账户状态（模拟，带幽默）"""
        # 根据账户名的hash值模拟不同状态
        status_code = hash(account) % 4
        statuses = [
            "账户状态：正常 ✅ 您的账户一切正常，可以放心使用！",
            "账户状态：VIP会员 🌟 恭喜您是我们的VIP会员，享受更多特权！",
            "账户状态：待激活 ⏳ 账户需要激活，请完成邮箱验证（开玩笑的，其实已经激活了😄）",
            "账户状态：正常 ✅ 账户状态良好，就像今天的天气一样晴朗！"
        ]
        return statuses[status_code]
    
    def _get_humor_response(self, context: str) -> str:
        """获取幽默回复"""
        humor_responses = [
            "哈哈，这个问题问得好！",
            "让我想想...（假装思考中🤔）",
            "这个问题有点意思，让我来帮您解决！",
            "好的，我明白了！虽然我是机器人，但我很聪明的😎",
            "没问题！虽然我不能喝咖啡，但我可以24小时为您服务☕",
            "收到！正在处理中...（其实我已经处理完了，就是想让你等一秒😏）"
        ]
        # 根据context的hash值选择不同的幽默回复
        index = hash(context) % len(humor_responses)
        return humor_responses[index]
    
    def _calculate_discount(self, price: str, discount_type: str) -> str:
        """计算折扣（模拟，带幽默）"""
        try:
            original_price = float(price)
        except:
            return "价格格式有误，请重新输入"
        
        discounts = {
            "新用户": 0.1,  # 10%折扣
            "VIP": 0.2,     # 20%折扣
            "节日": 0.15,   # 15%折扣
            "默认": 0.05   # 5%折扣
        }
        
        discount_rate = discounts.get(discount_type, discounts["默认"])
        final_price = original_price * (1 - discount_rate)
        saved = original_price - final_price
        
        return f"原价：{original_price:.2f}元，{discount_type}折扣：{discount_rate*100:.0f}%，最终价格：{final_price:.2f}元（省了{saved:.2f}元，可以买杯奶茶了🥤）"
    
    def _get_follow_up_question(self, topic: str) -> str:
        """生成追问问题（基于话题）"""
        # 如果topic是意图名称，提取关键词
        topic_key = topic
        if "查询" in topic or "订单" in topic:
            topic_key = "订单"
        elif "退款" in topic:
            topic_key = "退款"
        elif "商品" in topic or "推荐" in topic:
            topic_key = "商品"
        elif "账户" in topic:
            topic_key = "账户"
        elif "优惠" in topic or "券" in topic:
            topic_key = "优惠"
        
        follow_ups = {
            "订单": "您还想了解订单的其他信息吗？比如物流详情、预计送达时间、配送方式等？",
            "退款": "关于退款，您还有其他问题吗？比如退款到账时间、退款方式、退款进度查询等？",
            "商品": "您还想了解这个商品的更多信息吗？比如详细规格、用户评价、使用说明、保修政策等？",
            "账户": "关于账户，您还想了解什么？比如会员权益、积分查询、等级提升、专属优惠等？",
            "优惠": "关于优惠，您还想了解什么？比如更多优惠券、限时活动、会员专享折扣等？",
            "默认": "您还想了解其他相关信息吗？"
        }
        return follow_ups.get(topic_key, follow_ups["默认"])
    
    def _get_related_topic(self, current_topic: str) -> str:
        """获取相关话题（话题发散）"""
        # 如果topic是意图名称，提取关键词
        topic_key = current_topic
        if "查询" in current_topic or "订单" in current_topic:
            topic_key = "订单"
        elif "退款" in current_topic:
            topic_key = "退款"
        elif "商品" in current_topic or "推荐" in current_topic:
            topic_key = "商品"
        elif "账户" in current_topic:
            topic_key = "账户"
        elif "优惠" in current_topic or "券" in current_topic:
            topic_key = "优惠"
        
        related_topics = {
            "订单": "除了订单查询，您可能还想了解：物流跟踪、订单修改、发票申请、订单评价等服务",
            "退款": "除了退款，您可能还想了解：换货服务、商品评价、售后服务、质量问题处理等",
            "商品": "除了商品推荐，您可能还想了解：优惠活动、新品上架、限时特价、品牌故事等",
            "账户": "除了账户查询，您可能还想了解：会员升级、积分兑换、优惠券领取、专属客服等",
            "优惠": "除了优惠券，您可能还想了解：会员折扣、限时活动、满减优惠、生日特权等",
            "默认": "您可能还想了解我们的其他服务，比如优惠活动、新品推荐、会员权益等"
        }
        return related_topics.get(topic_key, related_topics["默认"])
    
    def _get_logistics_info(self) -> str:
        """获取物流信息（模拟）"""
        import random
        statuses = [
            "订单已发货，正在运输途中",
            "订单已到达配送中心，准备派送",
            "订单正在派送中，预计今天送达",
            "订单已由快递员揽收，正在配送",
        ]
        return random.choice(statuses)
    
    def _get_refund_status(self) -> str:
        """获取退款状态（模拟）"""
        import random
        statuses = [
            "退款申请已审核通过，正在处理中",
            "退款已提交到财务部门，预计2-3个工作日到账",
            "退款处理中，请耐心等待",
            "退款申请已批准，资金正在退回",
        ]
        return random.choice(statuses)
    
    def _get_more_coupons(self) -> str:
        """获取更多优惠信息（模拟）"""
        import random
        coupons = [
            "当前有满100减20的限时活动，还有新用户专享50元优惠券",
            "会员专享折扣正在进行中，生日用户可领取100元生日特权券",
            "限时活动：满200减50，还有积分兑换优惠券活动",
            "新用户注册即送30元优惠券，会员可享受9折优惠",
        ]
        return random.choice(coupons)
    
    def _get_product_details(self) -> str:
        """获取商品详情（模拟）"""
        import random
        details = [
            "该商品拥有详细的技术规格参数，用户评价4.8分，提供1年质保服务",
            "商品规格齐全，已有500+用户好评，支持7天无理由退货，3年保修",
            "产品参数详细，用户满意度高，提供完整的使用说明和售后保障",
            "规格参数完整，用户评价优秀，享受全国联保和免费技术支持",
        ]
        return random.choice(details)
    
    def _get_member_benefits(self) -> str:
        """获取会员权益（模拟）"""
        import random
        benefits = [
            "您当前是VIP会员，拥有1000积分，可享受9折优惠和专属客服",
            "您的会员等级为黄金会员，积分余额500，享有生日特权和专属优惠",
            "您是普通会员，当前积分200，升级后可享受更多专属权益",
            "您的会员状态正常，拥有800积分，可参与积分兑换活动",
        ]
        return random.choice(benefits)
    
    def _get_personalized_recommendation(self, user_preference: str, category: str = "") -> str:
        """获取个性化推荐（模拟）"""
        import random
        recommendations = {
            "手机": [
                "根据您的偏好，为您推荐：最新款旗舰手机，配备顶级处理器和超清摄像头，性价比极高！",
                "基于您的浏览历史，推荐这款热销手机：性能强劲，拍照出色，用户好评如潮！",
            ],
            "电脑": [
                "根据您的需求，推荐这款高性能笔记本：办公游戏两不误，轻薄便携，续航持久！",
                "为您精选：专业级笔记本电脑，配置强大，适合您的使用场景！",
            ],
            "耳机": [
                "为您推荐：降噪蓝牙耳机，音质卓越，佩戴舒适，是您通勤路上的好伙伴！",
                "基于您的偏好，推荐这款高性价比耳机：音质清晰，续航持久，价格美丽！",
            ],
        }
        if category in recommendations:
            return random.choice(recommendations[category])
        return f"根据您的偏好'{user_preference}'，为您推荐精选好物，品质保证，总有一款适合您！✨"
    
    def _calculate_shipping_fee(self, address: str, weight: str = "1") -> str:
        """计算运费（模拟）"""
        import random
        try:
            weight_kg = float(weight)
        except:
            weight_kg = 1.0
        
        # 根据地址和重量计算运费
        base_fee = 10.0
        weight_fee = weight_kg * 2.0
        total_fee = base_fee + weight_fee
        
        regions = {
            "北京": 0, "上海": 0, "广州": 0, "深圳": 0,
            "杭州": 5, "南京": 5, "成都": 8, "武汉": 8,
        }
        region_fee = 0
        for city, fee in regions.items():
            if city in address:
                region_fee = fee
                break
        
        total = total_fee + region_fee
        return f"运费计算：基础运费{base_fee}元 + 重量费{weight_fee:.1f}元 + 地区费{region_fee}元 = 总计{total:.1f}元"
    
    def _get_promotion_info(self, promotion_type: str) -> str:
        """获取促销信息（模拟）"""
        import random
        promotions = {
            "限时": [
                "🔥 限时特惠：全场商品8折起，仅限今天！错过再等一年！",
                "⏰ 限时抢购：热门商品低至5折，库存有限，先到先得！",
            ],
            "节日": [
                "🎉 节日大促：满200减50，满500减150，更有神秘礼品等你来拿！",
                "🎁 节日特惠：全场9折，会员再享9.5折，双重优惠不容错过！",
            ],
            "会员": [
                "👑 会员专享：VIP会员全场8.5折，积分翻倍，专属客服优先处理！",
                "⭐ 会员特权：黄金会员享受9折优惠，生日月额外赠送100积分！",
            ],
        }
        if promotion_type in promotions:
            return random.choice(promotions[promotion_type])
        return "当前有多个促销活动正在进行，详情请咨询客服或查看活动页面！"
    
    def _check_inventory(self, product_name: str) -> str:
        """检查库存（模拟）"""
        import random
        statuses = [
            f"商品'{product_name}'库存充足，有500+件现货，可立即发货！",
            f"商品'{product_name}'库存紧张，仅剩50件，建议尽快下单！",
            f"商品'{product_name}'暂时缺货，预计3-5个工作日补货，可先预订！",
            f"商品'{product_name}'有现货，库存100件，支持全国包邮！",
        ]
        return random.choice(statuses)
    
    def _get_after_sales_service(self, service_type: str) -> str:
        """获取售后服务信息（模拟）"""
        import random
        services = {
            "换货": [
                "换货服务：7天内可申请换货，支持同款不同规格或不同颜色，免费上门取件！",
                "换货政策：商品有质量问题可申请换货，我们提供免费换货服务，全程无忧！",
            ],
            "维修": [
                "维修服务：商品在保修期内享受免费维修，全国联保，专业维修团队！",
                "维修保障：提供1-3年质保服务，维修期间提供备用机，让您使用无忧！",
            ],
            "退货": [
                "退货服务：7天无理由退货，商品未使用可申请退货，退款3-5个工作日到账！",
                "退货保障：支持7天无理由退货，商品完好可全额退款，运费由我们承担！",
            ],
        }
        if service_type in services:
            return random.choice(services[service_type])
        return "我们提供完善的售后服务，包括换货、维修、退货等，详情请咨询客服！"
    
    def _get_user_preferences(self, user_id: str) -> str:
        """获取用户偏好（模拟）"""
        import random
        preferences = [
            "根据您的浏览记录，您偏好：电子产品、数码配件、智能家居类商品",
            "基于您的购买历史，推荐：时尚服饰、美妆护肤、生活用品等类别",
            "您的偏好：运动健身、户外装备、健康食品等生活方式类商品",
            "根据您的收藏，您喜欢：图书音像、文创用品、手工艺品等文化类商品",
        ]
        return random.choice(preferences)
    
    def _format_price(self, price: str) -> str:
        """格式化价格显示"""
        try:
            price_float = float(price)
            return f"¥{price_float:,.2f}".replace(",", ",")
        except:
            return f"¥{price}"

