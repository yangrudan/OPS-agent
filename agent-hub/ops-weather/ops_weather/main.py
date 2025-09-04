from mofa.agent_build.base.base_agent import MofaAgent, run_agent
import requests

@run_agent
def run(agent:MofaAgent):
    # task可以作为位置信息传入
    task = agent.receive_parameter('task')
    
    url = "https://eolink.o.apispace.com/456456/weather/v001/now"

    payload = {"lonlat" : "121.4581,31.2222"}

    headers = {
        "X-APISpace-Token":"YOUR KEY"
    }

    response=requests.request("GET", url, params=payload, headers=headers)

    agent_output_name = 'agent_result'
    agent.send_output(agent_output_name=agent_output_name,agent_result=response.text)
def main():
    agent = MofaAgent(agent_name='ops-weather')
    run(agent=agent)
if __name__ == "__main__":
    main()
