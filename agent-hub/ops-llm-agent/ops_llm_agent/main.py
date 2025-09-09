from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from openai import OpenAI
import os

from .multi_llm import choice_and_run_llm_model


def identify_info_types(user_input):
    """
    识别 user_input 包含的信息类型
    返回值：信息类型列表（如 ["用药", "天气", "安全警报"]）
    """
    info_types = []
    # 1. 匹配「用药信息」关键词（可根据实际输入补充更多关键词）
    medicine_keywords = ["药", "吃药", "服药", "剂量", "注意事项", "硝苯地平", "降压药", "感冒药"]
    if any(keyword in user_input for keyword in medicine_keywords):
        info_types.append("用药")
    
    # 2. 匹配「天气信息」关键词
    weather_keywords = ["天气", "温度", "晴", "雨", "雪", "风", "高温", "降温", "湿度"]
    if any(keyword in user_input for keyword in weather_keywords):
        info_types.append("天气")
    
    # 3. 匹配「安全警报信息」关键词（如居家安全、紧急情况等）
    safety_keywords = ["心率", "警报", "安全", "漏水", "漏气", "摔倒", "紧急", "求助", "异常", "火灾", "盗窃"]
    if any(keyword in user_input for keyword in safety_keywords):
        info_types.append("安全警报")
    
    return info_types if info_types else ["其他"]  # 无匹配时返回「其他」


def generate_dynamic_llm_content(info_types):
    """
    根据信息类型动态生成 llm_content（系统提示词）
    参数：info_types - 识别出的信息类型列表
    返回值：适配当前输入的系统提示词
    """
    # --------------------------
    # 1. 基础模板（所有场景通用）
    # --------------------------
    base_template = """你是一位专注服务老年人的生活助手，擅长用亲切、易懂的口语化表达（避免复杂术语，句子简短，像家人叮嘱一样温和）输出信息。"""
    
    # --------------------------
    # 2. 各类型专属模板（聚焦核心任务）
    # --------------------------
    templates = {
        "用药": """
        【用药信息处理要求】
        1. 优先提取老人用药关键信息：药名、服用时间（如“每天早7点”）、剂量（如“每次1片”）、注意事项（如“不可与柚子同食”）；
        2. 用药提醒需突出“安全”：明确禁忌、漏服处理（若有相关信息），用“记得哦”“别忘啦”等语气强化记忆；
        3. 若有多种药物，按服用时间顺序整理（如“早上吃XX，晚上吃XX”）。
        """,
        
        "天气": """
        【天气信息处理要求】
        1. 提取天气核心信息：温度范围（如“18-25℃”）、天气类型（如“晴/小雨”）、风力（如“微风”）；
        2. 结合天气给老人提具体生活建议：高温提醒“多喝温水、少出门”，雨天提醒“穿防滑鞋、别打湿衣服”，降温提醒“添件外套、别着凉”；
        3. 建议要贴合老人行动特点（如“出门记得带折叠伞，轻便好拿”）。
        """,
        
        "安全警报": """
        【安全警报信息处理要求】
        1. 优先提取警报核心：警报类型（如“漏水”“摔倒”“漏气”）、发生位置（如“厨房”“卧室”）、紧急程度（如“轻微漏水”“严重漏气”）；
        2. 给出老人能操作的简单应对步骤：非紧急情况（如“轻微漏水”）提示“先关紧水龙头，用抹布擦干地面”；紧急情况（如“燃气漏气”）提示“立即打开窗户通风，别碰电源开关，走到门外联系家人”；
        3. 语气要冷静安抚，避免恐慌，最后加一句“别着急，按步骤做就好”。
        """,
        
        "其他": """
        【其他信息处理要求】
        1. 用简单的话复述老人提供的信息，确保意思准确；
        2. 补充一句贴心提醒（如“有不清楚的地方可以再告诉我哦”）；
        3. 保持语气亲切，让老人感受到关心。
        """
    }
    
    # --------------------------
    # 3. 拼接模板（基础模板 + 各类型专属模板）
    # --------------------------
    dynamic_content = base_template
    for info_type in info_types:
        dynamic_content += templates[info_type]
    
    # --------------------------
    # 4. 补充多类型整合逻辑（若输入包含多种信息）
    # --------------------------
    if len(info_types) >= 2 and "其他" not in info_types:
        dynamic_content += """
        【多信息整合要求】
        按“紧急程度/优先级”排序输出：
        1. 若有“安全警报”，优先放在最前面（安全第一）；
        2. 其次放“用药提醒”（按时吃药很重要）；
        3. 最后放“天气建议”；
        4. 各部分用“先说说XX事哦”“再提醒你XX”过渡，让内容连贯不生硬。
        """
    
    return dynamic_content.strip()  # 去除多余空格，保持提示词简洁

@run_agent
def run(agent: MofaAgent):
    try:
        # 接收用户输入
        receive_data = agent.receive_parameters(['mem_data','weather_data','miband_data'])
        user_input = receive_data.get('mem_data')
        print(f"llm get mem info {user_input}")
        weather_input = receive_data.get('weather_data')
        print(f"llm get weather info {weather_input}")

        miband_input = receive_data.get('miband_data')
        print(f"llm get miband info {miband_input}")

        # # 步骤1：识别输入信息类型
        # info_types = identify_info_types(user_input)
        # print(f"识别到的信息类型：{info_types}")

        # info_types_2do = identify_info_types(weather_input)
        # print(f"识别到的222信息类型：{info_types_2do}")

        info_types = identify_info_types(user_input + " " + weather_input + " " + miband_input)

        # 步骤2：动态生成系统提示词
        llm_content = generate_dynamic_llm_content(info_types)
        print(f"动态生成的 llm_content：\n{llm_content}")

        # 步骤3：调用 LLM（与原代码一致）
        response = choice_and_run_llm_model(llm_content, user_input + " " + weather_input + " " + miband_input)
        
        # 发送输出
        agent.send_output(
            agent_output_name='llm_result',
            agent_result=response
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
