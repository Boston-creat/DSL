# 技术支持场景脚本
intent "技术支持" {
    when user_says "故障" or "问题" or "无法使用" or "需要帮助" or "技术支持" {
        ask "请描述您遇到的问题"
        wait_for problem_description
        set ticket_id = create_ticket(problem_description)
        response "已为您创建工单 {ticket_id}，我们的技术支持团队将在24小时内联系您"
    }
}

