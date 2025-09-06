import argparse
import json
import os
import ast
import sys
import websocket
import hashlib
import base64
import hmac
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
import _thread as thread
import pyaudio
import click
import pyarrow as pa
from dora import Node
from mofa.utils.install_pkg.load_task_weaver_result import extract_important_content
import threading

RUNNER_CI = True if os.getenv("CI") == "true" else False

# 语音识别相关常量和类
STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret):
        print("!!!! init wsParam")
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.CommonArgs = {"app_id": self.APPID}
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo":1,"vad_eos":10000}

    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f"api_key=\"{self.APIKey}\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", signature=\"{signature_sha}\""
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        url = url + '?' + urlencode(v)
        return url

# 全局变量
recognized_text = ""
is_recognition_complete = False
wsParam = None  # 全局wsParam变量

def on_message(ws, message):
    global recognized_text, is_recognition_complete
    try:
        msg = json.loads(message)
        code = msg["code"]
        sid = msg["sid"]
        if code != 0:
            errMsg = msg["message"]
            print(f"sid:{sid} call error:{errMsg} code is:{code}")
        else:
            data = msg["data"]["result"]["ws"]
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            
            if result not in ['。', '.。', ' .。', ' 。']:
                recognized_text += result
                print(f"识别结果: {result}")
                global is_recognition_complete
                is_recognition_complete = True
    except Exception as e:
        print(f"接收消息解析异常: {e}")

def on_error(ws, error):
    print(f"### 错误: {error}")

def on_close(ws, code, reason):
    global is_recognition_complete
    is_recognition_complete = True
    print(f"### 连接已关闭 ###")
    print(f"  状态码: {code}")
    # 修复：reason可能是字符串或bytes，统一处理
    if isinstance(reason, bytes):
        print(f"  原因: {reason.decode('utf-8')}")
    else:
        print(f"  原因: {reason}")

def on_open(ws):
    # 嵌套函数中使用nonlocal声明，访问外层的ws_param
    def run(ws_param):
        status = STATUS_FIRST_FRAME
        CHUNK = 520
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("- - - - - - - 开始录音 ...- - - - - - - ")

        # 录音60秒超时
        for i in range(0, int(RATE/CHUNK*60)):
            buf = stream.read(CHUNK)
            if not buf:
                status = STATUS_LAST_FRAME
            
            if status == STATUS_FIRST_FRAME:
                # 使用传入的ws_param而非全局变量
                d = {"common": ws_param.CommonArgs,
                     "business": ws_param.BusinessArgs,
                     "data": {"status": 0, "format": "audio/L16;rate=16000",
                              "audio": str(base64.b64encode(buf), 'utf-8'),
                              "encoding": "raw"}}
                ws.send(json.dumps(d))
                status = STATUS_CONTINUE_FRAME
            elif status == STATUS_CONTINUE_FRAME:
                d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                              "audio": str(base64.b64encode(buf), 'utf-8'),
                              "encoding": "raw"}}
                ws.send(json.dumps(d))
            elif status == STATUS_LAST_FRAME:
                d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                              "audio": str(base64.b64encode(buf), 'utf-8'),
                              "encoding": "raw"}}
                ws.send(json.dumps(d))
                time.sleep(1)
                break

        stream.stop_stream()
        stream.close()
        p.terminate()
        ws.close()
    
    # 启动线程时传入当前的wsParam
    global wsParam
    thread.start_new_thread(run, (wsParam,))

def start_voice_recognition():
    global recognized_text, is_recognition_complete, wsParam
    recognized_text = ""
    is_recognition_complete = False
    
    # 替换为你的实际参数
    wsParam = Ws_Param(
        APPID='7c0085db', 
        APIKey='171b10874c4e8b995494cb16729735d8',
        APISecret='OWQ0ZWIyODM3MzNlNjRhNzMzMDFjNmIy'
    )
    
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, 
                               on_message=on_message, 
                               on_error=on_error, 
                               on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, ping_timeout=2)
    
    while not is_recognition_complete:
        time.sleep(0.1)
    
    return recognized_text

def clean_string(input_string: str):
    return input_string.encode('utf-8', 'replace').decode('utf-8')

def send_task_and_receive_data(node):
    TIMEOUT = 300
    while True:
        print("请说话，开始录音...")
        data = start_voice_recognition()
        
        if not data:
            print("未识别到有效内容，请重试")
            continue
            
        print(f"发送任务: {data}")
        node.send_output("data", pa.array([clean_string(data)]))
        
        event = node.next(timeout=TIMEOUT)
        if event is not None:
            while True:
                if event is not None:
                    # print(f"aaaa {event}\n")
                    node_results = json.loads(event['value'].to_pylist()[0])
                    results = node_results.get('node_results')
                    is_dataflow_end = node_results.get('dataflow_status', False)
                    step_name = node_results.get('step_name', '')
                    click.echo(f'-------------{step_name}---------------')
                    click.echo(f"{results} ", )
                    click.echo(f'---------------------------------------')
                    sys.stdout.flush()
                    if is_dataflow_end in (True, 'true', 'True'):
                        break
                    event = node.next(timeout=TIMEOUT)
                else:
                    time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Simple arrow sender with voice input")

    parser.add_argument(
        "--name",
        type=str,
        required=False,
        help="The name of the node in the dataflow.",
        default="real-voice",
    )
    parser.add_argument(
        "--data",
        type=str,
        required=False,
        help="Arrow Data as string.",
        default=None,
    )

    args = parser.parse_args()

    data = os.getenv("DATA", args.data)

    node = Node(args.name)

    if data is None and os.getenv("DORA_NODE_CONFIG") is None:
        send_task_and_receive_data(node)

if __name__ == "__main__":
    main()
    