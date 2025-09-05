# OPS(Old People's) Agent

> 背景：toB 系列产品，旨在为老年人提供便捷、安全的智能生活体验。OPS Agent 致力于提升老年人的生活质量与安全性。
>
![logo](./docs/ops-logo.jpg)

💡 OPS Agent 是基于[**mofa-ai**](https://github.com/mofa-org/mofa)框架设计与打造， 专为老年人设计的智能助手，遵循成为老年人的守护者的初心，为其提供覆盖**记忆**、 **健康**、 **天气**三大类型的核心服务。

## 核心功能

- 记忆：帮助老年人记住重要信息，如用药习惯、亲朋的联系方式等。
- 健康：实时上报心率数据, 由llm进行处理分析。
- 天气：提供实时天气信息，帮助老年人合理安排出行和活动。

## 创新设计

- **自然语言交互**：老年人可以通过语音或文字与OPS Agent进行交流，无需复杂的操作。
- **硬件集成**：通过蓝牙BLE协议与MiBand6手环设备进行集成, 实时上报健康数据。
- **向量数据库**：应用北京智源研究院BAAI/bge模型和向量数据库存储和检索，确保信息的准确性和安全性。
- **中心调度节点**：ops-scheduler 作为中心调度节点，与记忆模块, 智能硬件设备, 天气MCP服务无缝对接。

## 关键数据流说明（按场景拆解）

🌳 OPS Agent系统通过中心调度节点(ops-scheduler)协调各模块：

1. 接收用户输入（语音/文本）
2. 分发请求到记忆/天气模块
3. 与智能硬件设备交互

详细数据流图请参考：[OPS Agent 数据流图](./examples/ops-agent/ops_agent_dataflow-graph.html)

## 安装与使用

🚀 快速开始

```bash
# 准备框架
pip install mofa-ai

# 准备ops agents
git clone https://github.com/yangrudan/OPS-agent.git
cd examples/ops-agent
dora up
dora build ops_agent_dataflow.yml
dora start ops_agent_dataflow.yml

# 另一个终端
mock-voice
李爷爷 吃药时间
```

## 难点和突破

基于向量数据库的模糊搜索和阈值动态调整

## 感谢

感谢以下项目提供的支持：

- [mofa-ai](https://github.com/mofa-org/mofa)
- [BAAI/bge](https://huggingface.co/BAAI/bge-small-zh)
- [MiBAND](https://github.com/mengxin239/miband4-heartrate)
- [天气API](https://www.apispace.com/)

## 贡献

欢迎您的加入，共同为OPS Agent的发展贡献力量！

## 展望

1. 支持更多外设设备接入，如智能手表等.
2. 支持更多场景，如新闻播报, 戏曲播放, 日常规划, 购物提醒等.
3. 加强安全模块建设, 如判断老人遇到危险时, 进行紧急联系人的呼叫.
4. 提高语音识别和自然语言处理能力，比如对方言更好的识别, 以实现更智能的交互.
