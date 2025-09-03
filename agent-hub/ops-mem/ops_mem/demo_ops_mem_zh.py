import json
import os
from ops_memory_zh import OPSMemoryAgent

def main():
    # 配置文件路径（确保正确）
    config_path = os.path.join(os.path.dirname(__file__), "configs", "ops_memory.yml")
    # 初始化OPS记忆代理
    memory_agent = OPSMemoryAgent(config_path)

    # 1. 存储3条中文记忆（OPS项目的核心场景）
    print("=== 开始存储记忆 ===")
    memory_agent.add_memory(
        content="李爷爷，每天早上8点吃降压药，每次1片，饭后服用",
        metadata={"type": "健康管理-用药", "user": "李爷爷", "priority": "high"}
    )
    memory_agent.add_memory(
        content="王奶奶，每天晚上7点看戏曲频道，喜欢《贵妃醉酒》选段",
        metadata={"type": "习惯记忆-作息", "user": "王奶奶"}
    )
    memory_agent.add_memory(
        content="李爷爷的孙女生日是6月1日，去年送了绘本作为礼物",
        metadata={"type": "关系维护-生日", "user": "李爷爷"}
    )

    # 2. 搜索中文记忆（模拟实际查询场景）
    print("\n=== 开始搜索记忆 ===")
    # 搜索1：查询李爷爷的用药信息
    drug_results = memory_agent.search_memory(query="李爷爷 用药时间")
    print("🔍 搜索'李爷爷 用药时间'结果：")
    for idx, res in enumerate(drug_results, 1):
        print(f"  {idx}. 内容：{res['content']} | 类型：{res['metadata']['type']}")

    # 搜索2：查询所有与"奶奶"相关的记忆
    grandma_results = memory_agent.search_memory(query="奶奶", similarity_threshold=0.5)
    print("\n🔍 搜索'奶奶'结果：")
    for idx, res in enumerate(grandma_results, 1):
        print(f"  {idx}. 内容：{res['content']} | 类型：{res['metadata']['type']}")

if __name__ == "__main__":
    main()