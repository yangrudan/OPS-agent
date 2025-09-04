import os

from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from .ops_memory_zh import OPSMemoryAgent


@run_agent
def run(agent:MofaAgent, memory_agent:OPSMemoryAgent):
    user_query = agent.receive_parameter('query')

    drug_results = memory_agent.search_memory(query=user_query)
    print("🔍 搜索结果：")
    for idx, res in enumerate(drug_results, 1):
        print(f"  {idx}. 内容：{res['content']} | 类型：{res['metadata']['type']}")

    agent_output_name = 'ops_mem_result'
    agent.send_output(agent_output_name=agent_output_name,agent_result=drug_results)
    print(f"📤 !!!!2222mem 已发送到输出节点 '{agent_output_name}'")
        
def main():
    agent = MofaAgent(agent_name='ops-mem')
     # 配置文件路径（确保正确）
    config_path = os.path.join(os.path.dirname(__file__), "configs", "ops_memory.yml")
    # 初始化OPS记忆代理
    memory_agent = OPSMemoryAgent(config_path)
    run(agent=agent, memory_agent=memory_agent)
    
if __name__ == "__main__":
    main()
