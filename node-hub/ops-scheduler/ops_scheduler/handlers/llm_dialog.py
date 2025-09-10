
def handle_llm_dialog(agent, text):
    agent.send_output(
        agent_output_name='query',
        agent_result={"query": text}
    )