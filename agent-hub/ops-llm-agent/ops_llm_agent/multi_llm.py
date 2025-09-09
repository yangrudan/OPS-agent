import os
from dotenv import load_dotenv
from openai import OpenAI


def choice_and_run_llm_model(llm_content, user_input):
    """
    根据环境变量选择并运行 LLM 模型
    """
    # 加载环境变量
    load_dotenv('.env.secret')
    llm_name =  os.getenv("USE_WHICH_LLM", "baidu")
    
    if llm_name == "baidu":
        print("Using Baidu LLM model...")
        return run_baidu_llm(llm_content, user_input)
    elif llm_name == "kimi":
        print("Using Kimi LLM model...")
        return run_kimi_llm(llm_content, user_input)
    else:
        pass # 可扩展更多模型

def run_baidu_llm(llm_content, user_input):
    client = OpenAI(
        base_url='https://qianfan.baidubce.com/v2',
        api_key=os.getenv('LLM_API_KEY')
    )
    response = client.chat.completions.create(
        model="qianfan-vl-8b", 
        messages=[
        {   
            "role": "user",
            "content": user_input
        },  
        {   
            "role": "assistant",
            "content": llm_content
        }   
    ], 
        temperature=0.000001, 
        top_p=1,
        extra_body={ 
            "repetition_penalty":1.05, 
            "frequency_penalty":0, 
            "presence_penalty":0
        }   
    )
    return response.choices[0].message.content


def run_kimi_llm(llm_content, user_input):

    # 初始化 OpenAI 客户端
    client = OpenAI(
        api_key=os.getenv('LLM_API_KEY'),
        base_url=os.getenv('LLM_API_BASE')
    )

    response = client.chat.completions.create(
        model=os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
        messages=[
            {"role": "system", "content": llm_content},
            {"role": "user", "content": user_input}
        ],
        stream=False
    )
    return response.choices[0].message.content
