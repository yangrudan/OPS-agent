from mofa.agent_build.base.base_agent import MofaAgent, run_agent
import asyncio
from bleak import BleakScanner, BLEDevice

# BLE设备配置
TARGET_DEVICE = "C5:CC:7D:AC:31:C2"
SAVE_TO_FILENAME = "heart_rate_data.txt"
SCAN_INTERVAL = 1 # 采集间隔（秒）
COLLECT_COUNT = 5   # 采集次数

class BLEHeartRateCollector:
    def __init__(self):
        self.latest_heart_rate = None
        self.scanner = None
        self.running = False
        self.collect_count = 0  # 已采集次数计数器

    def callback(self, sender: BLEDevice, advertisement_data):
        """BLE设备广播数据回调函数"""
        if sender.address == TARGET_DEVICE:
            # 提取心率数据（根据实际设备协议调整索引）
            try:
                data_bytes = advertisement_data.manufacturer_data[343]
                self.latest_heart_rate = data_bytes[3]
                print(f"检测到心率: {self.latest_heart_rate} BPM")
                
                # 保存到文件
                with open(SAVE_TO_FILENAME, 'w') as f:
                    f.write(str(self.latest_heart_rate))
            except (KeyError, IndexError) as e:
                print(f"数据解析错误: {e}")

    async def start_scanning(self):
        """启动BLE扫描"""
        self.running = True
        self.scanner = BleakScanner(detection_callback=self.callback)
        await self.scanner.start()
        print("BLE扫描已启动...")

    async def stop_scanning(self):
        """停止BLE扫描"""
        if self.scanner:
            await self.scanner.stop()
        self.running = False
        print("BLE扫描已停止")

    async def collect_data_periodically(self, agent: MofaAgent):
        """周期性采集并发送数据，达到次数后退出"""
        try:
            while self.running and self.collect_count < COLLECT_COUNT:
                if self.latest_heart_rate is not None:
                    # 发送心率数据到Agent输出
                    agent.send_output(
                        agent_output_name='heart_rate_result',
                        agent_result={
                            'heart_rate': self.latest_heart_rate,
                            'count': self.collect_count + 1,
                            'total': COLLECT_COUNT,
                            'device': TARGET_DEVICE
                        }
                    )
                    self.collect_count += 1  # 增加计数
                    self.latest_heart_rate = None  # 重置，等待新数据
                
                # 如果还没采集完，继续等待下一次
                if self.collect_count < COLLECT_COUNT:
                    await asyncio.sleep(SCAN_INTERVAL)
                else:
                    break  # 采集完成，退出循环
        except Exception as e:
            print(f"采集循环错误: {e}")

@run_agent
def run(agent:MofaAgent):
    task = agent.receive_parameter('task')
    print(f"接收到任务: {task}")

    # 初始化BLE采集器
    collector = BLEHeartRateCollector()
    
    try:
        # 启动事件循环
        loop = asyncio.get_event_loop()
        
        # 启动扫描和周期性采集
        loop.run_until_complete(collector.start_scanning())
        loop.run_until_complete(collector.collect_data_periodically(agent))
    except KeyboardInterrupt:
        print("用户中断程序")
    finally:
        # 确保资源正确释放
        loop.run_until_complete(collector.stop_scanning())
    
    agent_output_name = 'miband_result'
    agent.send_output(agent_output_name=agent_output_name,agent_result=task)

def main():
    agent = MofaAgent(agent_name='ops-miband')
    run(agent=agent)

if __name__ == "__main__":
    main()
