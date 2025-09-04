
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from .handlers.memory import handle_memory_query
# from .handlers.weather import handle_weather_query
# from .handlers.safe import handle_safety_alert
# from .handlers.llm_dialog import LLMHandler 
import yaml
import os

# 加载调度配置
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "configs", "agent.yml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@run_agent
def run(agent: MofaAgent):
    config= None
    # config = load_config()
    while True:
        # 接收输入（支持多源：语音/硬件/定时任务）
        input_event = agent.receive_parameter('input_event')
        # llm_handler = LLMHandler()  # 初始化LLM处理器
        if not input_event:
            continue
        
        # 解析事件类型（根据内容判断场景）
        event_type = classify_event(input_event)
        
        # 分发到对应处理器
        if event_type == "memory":
            print("🧠 !!!准备进行记忆查询事件...")
            result = handle_memory_query(agent, input_event, config)
            print("🧠 !!!记忆查询结果：", result)
        elif event_type == "weather":
            pass
            # result = handle_weather_query(agent, input_event, config)
        elif event_type == "safety":
            pass
            # result = handle_safety_alert(agent, input_event, config)
        else:
            # 未知类型调用LLM处理
            # result = llm_handler.handle_dialog(input_event)
            # TODO
            # 补充LLM处理标记
            result["source"] = "llm_dialog"
        
        # 发送最终结果到输出节点（如语音TTS）
        print("📤 !!!!!!调度结果：", result)

        # agent.send_output(
        #     agent_output_name='scheduler_result',
        #     agent_result=result
        # )

def classify_event(input_event):
    """根据输入内容分类事件类型"""
    # 1. 先处理参数类型：若传入的是字符串，自动包装成字典（兼容两种输入场景）
    if isinstance(input_event, str):
        input_event = {"content": input_event}  # 转为 {"content": "李爷爷 吃药时间"}
    
    keywords = {
        "memory": ["记得", "忘记", "时间", "电话", "生日","吃药"],  # "时间" 属于 memory 分类
        "weather": ["天气", "温度", "下雨", "晴天", "出门"],
        "safety": ["血压", "紧急", "求助", "摔倒", "异常"]
    }
    
    # 2. 提取事件内容（此时 input_event 已确保是字典）
    content = input_event.get("content", "").strip()  # 去除首尾空格，避免空输入问题
    
    # 3. 匹配关键词，返回事件类型
    for event_type, kw_list in keywords.items():
        if any(kw in content for kw in kw_list):
            print(f"🕵️  事件分类：检测到关键词，归类为 '{event_type}' 事件")
            return event_type
    
    # 无匹配时返回 unknown
    print("🕵️  事件分类：未匹配到关键词，归类为 'unknown' 事件")
    return "unknown"

def main():
    agent = MofaAgent(agent_name='ops-scheduler')
    run(agent=agent)

if __name__ == "__main__":
    main()