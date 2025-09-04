from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from openai import OpenAI
import os
from dotenv import load_dotenv

@run_agent
def run(agent: MofaAgent):
    try:
        # 加载环境变量
        load_dotenv('.env.secret')
        
        # 初始化 OpenAI 客户端
        client = OpenAI(
            api_key=os.getenv('LLM_API_KEY'),
            base_url=os.getenv('LLM_API_BASE')
        )
        
        # 接收用户输入
        user_input = agent.receive_parameter('query')
        print(f"llm get info {user_input}")

        llm_content = "你是一位专注服务老年人的生活助手，擅长用亲切、易懂的口语化表达（避免复杂术语，句子简短）输出信息。请按以下要求处理我提供的内容：\
                      1. 先明确提取关键信息：   - 老人需服用的药物信息（药名、服用时间、剂量、注意事项）；\
                         - 家人相关信息（如家人是否陪同、家人叮嘱的事项、家人可提供的帮助）；\
                         - 当日天气情况（温度、天气类型如晴/雨/雪、风力等）。\
                      2. 按“用药提醒→结合天气的生活建议→家人关怀提示”的逻辑整合信息，确保内容连贯、有条理。\
                      3. 重点突出“用药安全”和“天气对老人的影响”（如雨天提醒防滑、高温提醒补水等），语言温和，像家人叮嘱一样亲切。"
        
        # 调用 LLM
        response = client.chat.completions.create(
            model=os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
            messages=[
                {"role": "system", "content": llm_content},
                {"role": "user", "content": user_input}
            ],
            stream=False
        )
        
        # 发送输出
        agent.send_output(
            agent_output_name='llm_result',
            agent_result=response.choices[0].message.content
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")
        # agent.logger.error(f"Error: {str(e)}")
        agent.send_output(
            agent_output_name='llm_result',
            agent_result=f"Error: {str(e)}"
        )

def main():
    agent = MofaAgent(agent_name='ops-llm-agent')
    run(agent=agent)

if __name__ == "__main__":
    main()
