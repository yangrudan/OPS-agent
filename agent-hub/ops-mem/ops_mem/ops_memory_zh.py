import os
import json
import time
import chromadb  # 直接使用chromadb原生库
from dotenv import load_dotenv
from mofa.agent_build.base.base_agent import run_agent,MofaAgent
from sentence_transformers import SentenceTransformer  # 直接用sentence-transformers生成向量
from chromadb.utils import embedding_functions  # Chroma的嵌入工具类
from mofa.utils.files.read import read_yaml

class OPSMemoryAgent:
    def __init__(self, config_path):
        self.yml_config = read_yaml(config_path)["agent"]
        self._load_env()

        # 1. 初始化中文嵌入模型（直接用sentence-transformers，不依赖mem0）
        self.embed_model = self._init_embed_model()

        # 2. 初始化Chroma向量库（直接用chromadb原生API，不依赖mem0）
        self.chroma_client, self.collection = self._init_chroma()

        # 初始化MOFA代理
        # self.agent = MofaAgent(agent_name='ops-memory-agent')

    def _load_env(self):
        load_dotenv('ops.env')
        self.user_id = os.getenv('MEMORY_ID', 'ops-admin')  # 区分用户
        self.memory_limit = int(os.getenv('MEMORY_LIMIT', 100))  # 记忆上限
        self.chroma_path = self.yml_config["vector_store"]["config"]["path"]  # Chroma存储路径
        self.collection_name = self.yml_config["vector_store"]["config"]["collection_name"]  # 集合名

    def _init_embed_model(self):
        """初始化中文嵌入模型（BAAI/bge-small-zh-v1.5）"""
        model_name = self.yml_config["embedder"]["config"]["model"]
        # 直接加载本地模型（首次运行自动下载到~/.cache/huggingface）
        return SentenceTransformer(model_name, device="cpu")  # 强制CPU运行

    def _init_chroma(self):
        """直接初始化Chroma客户端和集合（绕开mem0）"""
        # 1. 创建Chroma持久化客户端（数据存在本地路径）
        client = chromadb.PersistentClient(path=self.chroma_path)
        
        # 2. 获取或创建集合（若不存在则自动创建）
        # 注意：不指定embedding_function，后续手动传入向量
        collection = client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "OPS项目老年人记忆存储集合"}
        )
        print(f"✅ Chroma向量库初始化成功，集合名：{self.collection_name}，路径：{self.chroma_path}")
        return client, collection

    def add_memory(self, content, metadata=None):
        """添加记忆：手动生成向量，直接存入Chroma"""
        metadata = metadata or {}
        # 给记忆添加用户ID（确保搜索时只返回当前用户的记忆）
        metadata["user_id"] = self.user_id
        
        # 1. 手动生成中文内容的嵌入向量（用sentence-transformers）
        embedding = self.embed_model.encode(content, convert_to_tensor=False)
        
        # 2. 生成唯一ID（避免重复存储，格式：用户ID_时间戳）
        memory_id = f"{self.user_id}_{int(time.time() * 1000)}"  # 时间戳精确到毫秒
        
        # 3. 存入Chroma：id、向量、文本、元数据
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )
        print(f"✅ 已添加记忆（ID：{memory_id[:10]}...）：{content[:30]}...")

        # 修剪旧记忆
        self._prune_old_memory()

    def search_memory(self, query, limit=None,  similarity_threshold=0.6, person_filter=None):
        """搜索记忆：手动生成查询向量，在Chroma中匹配"""
        limit = limit or self.memory_limit
        
        # 1. 生成查询词的嵌入向量
        query_embedding = self.embed_model.encode(query, convert_to_tensor=False)

        # 构建过滤条件：用户ID + 人物标签（可选）
        filter_cond = {"user_id": self.user_id}
        if person_filter:
            # 模糊匹配人物标签（如person_filter="奶奶"，匹配含“奶奶”的person）
            filter_cond["person"] = {"$contains": person_filter}

        # 获取Chroma原始结果
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where={"user_id": self.user_id},
            include=["documents", "metadatas", "distances"]
        )
        #打印原始结果（重点看documents和metadatas是否有数据）
        print(f"📝 调试日志：Chroma返回原始结果：")
        print(f"  - 文档数量：{len(results['documents'][0])}")
        print(f"  - 文档内容：{results['documents'][0]}")
        print(f"  - 元数据：{results['metadatas'][0]}")
        print(f"  - 距离：{results['distances'][0]}")
        

        # 3. 计算相似度并过滤（Chroma返回的是cosine距离，相似度=1-距离）
        formatted_results = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        # 遍历结果，优化相似度计算
        for doc, meta, dist in zip(documents, metadatas, distances):
            if not doc:
                continue
            
            # 优化1：相似度计算（添加边界保护，确保在0-1区间）
            similarity = 1 - (dist / 2)
            similarity = max(similarity, 0.0)  # 避免相似度为负
            similarity = min(similarity, 1.0)  # 避免相似度超过1
            
            # 优化2：打印计算日志，便于调试
            # print(f"📊 相似度计算：关键词'{query}' vs 记忆'{doc[:20]}...'")
            # print(f"  - cosine距离：{round(dist, 3)}")
            # print(f"  - 计算相似度：{round(similarity, 3)}（阈值：{similarity_threshold}）")
            
            # 阈值过滤（使用优化后的相似度）
            if similarity >= similarity_threshold:
                # 提取元数据（兼容字段缺失场景）
                mem_type = meta.get("type", "未分类")
                formatted_results.append({
                    "content": doc,
                    "metadata": {"type": mem_type, **meta},
                    "similarity": round(similarity, 3)
                })
        
        # 按相似度降序排序
        formatted_results.sort(key=lambda x: x["similarity"], reverse=True)
        return formatted_results

    def _prune_old_memory(self):
        """修剪旧记忆：超出上限时删除最早的记忆（按ID中的时间戳排序）"""
        # 1. 查询当前用户的所有记忆（按ID升序，ID包含时间戳，最早的在前）
        all_memories = self.collection.get(
            where={"user_id": self.user_id},
            include=["metadatas"]  # 只需获取ID和元数据，无需向量和文本
        )
        memory_ids = all_memories["ids"]
        if len(memory_ids) <= self.memory_limit:
            return  # 未超出上限
        
        # 2. 计算需要删除的旧记忆数量和ID
        num_to_delete = len(memory_ids) - self.memory_limit
        old_ids = memory_ids[:num_to_delete]  # 取最早的N条ID
        
        # 3. 删除旧记忆
        self.collection.delete(ids=old_ids)
        print(f"🗑️  已修剪{num_to_delete}条旧记忆，当前剩余{len(memory_ids)-num_to_delete}条")

    def run(self):
        """运行MOFA代理，接收外部指令"""
        # @self.agent.run_agent
        def process(agent: MofaAgent):
            print("\n🚀 OPS记忆代理已启动，等待接收消息...")
            while True:
                message = agent.receive_parameter("ops_message")
                if not message:
                    continue
                
                # 解析JSON消息
                try:
                    msg_data = json.loads(message)
                except json.JSONDecodeError:
                    print("❌ 消息格式错误！需为JSON字符串（示例：{\"type\":\"store\",\"content\":\"xxx\"}）")
                    continue
                
                # 处理存储指令
                if msg_data.get("type") == "store":
                    content = msg_data.get("content")
                    if not content:
                        print("❌ 存储失败：记忆内容不能为空！")
                        continue
                    self.add_memory(
                        content=content,
                        metadata=msg_data.get("metadata", {})
                    )
                    # 返回存储状态
                    agent.send_output(
                        "memory_status",
                        agent_result=json.dumps({"status": "success", "msg": "记忆存储成功"}),
                        is_end_status=True
                    )
                
                # 处理搜索指令
                elif msg_data.get("type") == "search":
                    query = msg_data.get("query")
                    if not query:
                        print("❌ 搜索失败：查询词不能为空！")
                        continue
                    results = self.search_memory(query=query)
                    # 返回搜索结果
                    agent.send_output(
                        "search_results",
                        agent_result=json.dumps({
                            "status": "success",
                            "count": len(results),
                            "results": results
                        }),
                        is_end_status=True
                    )

if __name__ == "__main__":
    # 验证配置文件路径
    config_path = os.path.join(os.path.dirname(__file__), "configs", "ops_memory.yml")
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在！路径：{config_path}")
        print("💡 请执行 'ls configs/' 确认是否存在ops_memory.yml")
    else:
        ops_agent = OPSMemoryAgent(config_path)
        ops_agent.run()
