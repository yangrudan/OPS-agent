from mofa.agent_build.base.base_agent import MofaAgent, run_agent
import requests

@run_agent
def run(agent:MofaAgent):
    # task可以作为位置信息传入
    task = agent.receive_parameter('query')
    print("🌤️ !!!天气查询任务：", task)
    
    url = "https://eolink.o.apispace.com/456456/weather/v001/now"

    payload = {"lonlat" : "121.4581,31.2222"}

    headers = {
        "X-APISpace-Token":"n0xfkt3m1f1ddr3cf8f05bqijxilqugp"
    }

    response=requests.request("GET", url, params=payload, headers=headers)

    agent_output_name = 'ops_weather_result'
    agent.send_output(agent_output_name=agent_output_name,agent_result=response.text)
    print(f"📤 !!!!天气 已发送到输出节点 '{agent_output_name}' 内容是 {response.text}")
    
def main():
    agent = MofaAgent(agent_name='ops-weather')
    run(agent=agent)

if __name__ == "__main__":
    main()
