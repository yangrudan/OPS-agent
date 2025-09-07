def handle_memory_query(agent, input_event, config):
    """处理记忆查询：调用ops-mem模块并返回结果"""
    print("sssssssssssssssssss\n")
    # 1. 构造查询参数
    query = input_event
    # print(f"sssssssssssssssssss  {query}\n")
    print("🧠 00000 DEBUG: 记忆查询内容：", query)
    # if not query:
    #     return {"status": "error", "message": "查询内容为空"}
    
    print("🧠 111 DEBUG: 记忆查询内容：", query)
    # 2. 发送查询到ops-mem模块
    print("📤 !!!发送查询到ops-mem模块...")
    agent.send_output(
        agent_output_name='query',
        agent_result={"query": query}
    )

    # return {
    #     "status": "success",
    #     "message": "查询已发送到ops-mem模块，等待结果中..."
    # }
    
    # 3. 接收ops-mem返回结果
    # print("⏳ !!!等待ops-mem返回结果...")
    # mem_result = agent.receive_parameter('ops_mem_result')
    # if not mem_result:
    #     return {"status": "error", "message": "未获取到记忆数据"}
    
    # # 4. 格式化结果（适配老年人理解）
    # formatted_result = format_for_elderly(mem_result)
    # return {
    #     "status": "success",
    #     "original_result": mem_result,
    #     "formatted_result": formatted_result
    # }

def format_for_elderly(mem_result):
    """将记忆结果转换为老年人易懂的语言"""
    if not mem_result:
        return "没有找到相关信息哦~"
    return "\n".join([f"- {item['content']}" for item in mem_result[:3]])