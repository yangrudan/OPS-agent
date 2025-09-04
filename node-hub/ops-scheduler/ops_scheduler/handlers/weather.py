def handle_weather_query(agent, input_event, config):
    """调用ops-weather模块并返回结果"""

    # 1. 构造查询参数
    query = input_event
    if not query:
        return {"status": "error", "message": "查询内容为空"}
    
    # 2. 发送查询到ops-mem模块
    print("📤 !!!发送查询到ops-weather模块...")
    agent.send_output(
        agent_output_name='weather_query',
        agent_result={"query": query}
    )

    return {
        "status": "success",
        "message": "查询已发送到ops-weather模块，等待结果中..."
    }