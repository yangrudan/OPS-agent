from gradio_client import Client
import simpleaudio as sa
import time

def clean_text_for_tts(input_text):
    # 定义需要过滤或替换的无效字符
    invalid_chars = {'/', '℃', '\n'}
    # 替换或删除无效字符（根据需求调整策略）
    cleaned_text = input_text
    for char in invalid_chars:
        if char == '\n':
            cleaned_text = cleaned_text.replace(char, '。')  # 换行符替换为中文句号（保证断句自然）
        elif char == '℃':
            cleaned_text = cleaned_text.replace(char, '摄氏度')  # 符号替换为文字（确保正确发音）
        else:
            cleaned_text = cleaned_text.replace(char, '')  # 其他字符直接删除
    return cleaned_text

def arabic_to_chinese_num(text: str) -> str:
    """
    将字符串中的阿拉伯数字（0-9）替换为中文小写数字（零-九）
    
    参数:
        text: 包含阿拉伯数字的原始字符串
        
    返回:
        替换后的字符串
    """
    # 建立阿拉伯数字与中文数字的映射关系
    num_map = {
        '0': '零',
        '1': '一',
        '2': '二',
        '3': '三',
        '4': '四',
        '5': '五',
        '6': '六',
        '7': '七',
        '8': '八',
        '9': '九',
        '.': '点',
        '-': '到',
        '%': '百分比'
    }
    
    # 遍历映射表，逐个替换字符串中的阿拉伯数字
    for arabic_num, chinese_num in num_map.items():
        text = text.replace(arabic_num, chinese_num)
    
    return text

def get_raw_wav(text):
    try:
        # 尝试创建客户端连接
        client = Client("https://cb94260a5a0726758c.gradio.live/")
    except Exception as e:
        print(f"无法连接到服务: {str(e)}")
        print("可能的原因：服务未启动、网络问题或URL错误")
        return None

    try:
        clear_text_0 = arabic_to_chinese_num(text)
        clear_text = clean_text_for_tts(clear_text_0)
        print(f"clear_text: {clear_text}\n")
        
        # 尝试调用服务生成音频
        result = client.predict(
            clear_text,	# str  in 'Input Text' Textbox component
            0.3,	# float (numeric value between 1e-05 and 1.0) in 'Audio temperature' Slider component
            0.7,	# float (numeric value between 0.1 and 0.9) in 'top_P' Slider component
            20,	# float (numeric value between 1 and 20) in 'top_K' Slider component
            2,	# float  in 'Audio Seed' Number component
            42,	# float  in 'Text Seed' Number component
            True,	# bool  in 'Refine text' Checkbox component
                            api_name="/generate_audio"
        )

        print(result)
        
        # 检查结果是否有效
        if not result or len(result) == 0:
            print("服务返回空结果，可能服务不可用")
            return None
            
        wav_path = result[0]
        
        if wav_path.endswith('.wav'):
            print("这是一个有效的WAV文件路径")
        else:
            print("这不是一个WAV文件路径")
            # 检查是否包含服务错误信息
            if "无此服务" in str(wav_path) or "服务不可用" in str(wav_path):
                print(f"服务错误: {wav_path}")
                return None

        print(f"wav_path: {wav_path}")
        return wav_path
        
    except Exception as e:
        print(f"调用服务时发生错误: {str(e)}")
        print("可能的原因：服务暂时不可用、API变更或参数错误")
        return None


# def get_raw_wav(text):
#     client = Client("https://b8c48ae070eb82a207.gradio.live/")
#     clear_text = arabic_to_chinese_num(text)
#     print(f"clear_text: {clear_text}\n")
#     result = client.predict(
# 		clear_text,	# str  in 'Input Text' Textbox component
# 		0.3,	# float (numeric value between 1e-05 and 1.0) in 'Audio temperature' Slider component
# 		0.7,	# float (numeric value between 0.1 and 0.9) in 'top_P' Slider component
# 		20,	# float (numeric value between 1 and 20) in 'top_K' Slider component
# 		2,	# float  in 'Audio Seed' Number component
# 		42,	# float  in 'Text Seed' Number component
# 		True,	# bool  in 'Refine text' Checkbox component
# 							api_name="/generate_audio"
#     )

#     print(result)
#     wav_path = result[0]
#     if wav_path.endswith('.wav'):
#         print("这是一个有效的WAV文件路径")
#     else:
#         print("这不是一个WAV文件路径")

#     print(f"wav_path: {wav_path}")
#     return wav_path

def play_wav(file_path):
    wave_obj = sa.WaveObject.from_wave_file(file_path)
    # 播放音频
    play_obj = wave_obj.play()
    # 等待播放完成
    play_obj.wait_done()

def get_and_play_wav(text):
    if "401" in text:
        print("检测到 401 错误")
        return
    
    wav_path = get_raw_wav(text)
    print(f"!!wav_path: {wav_path}")

    if wav_path is None:
        print("无法获取WAV文件")
        return
    # time.sleep(3)  # 确保文件已保存
    play_wav(str(wav_path))

if __name__ == "__main__":
    test_text = "爷爷奶奶们，记得哦，您每天早上8点要按时吃药，每次就吃1片，要在吃完饭后服用。这样对身体好，别忘啦！"
    get_and_play_wav(test_text)
