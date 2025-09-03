import os
from openai import OpenAI  # 以OpenAI为例，可替换为本地LLM
from dotenv import load_dotenv


class LLMHandler:
    def __init__(self):
        load_dotenv('.env.secret')

        self.client = OpenAI(
            api_key=os.getenv('LLM_API_KEY'),
            base_url=os.getenv('LLM_API_BASE')
        )
        self.system_prompt = """
        你是老年人智能助手，需要用简洁易懂的口语化中文回应。
        回答要亲切、有耐心，避免专业术语，语速适中。
        """

    def handle_dialog(self, query):
        """调用LLM处理未知类型查询"""
        load_dotenv('.env.secret')
        
        try:
            response = self.client.chat.completions.create(
                model=os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": query}
                ],
                stream=False
            )
            
            return {
                "status": "success",
                "content": response.choices[0].message.content
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"对话处理失败：{str(e)}"
            }