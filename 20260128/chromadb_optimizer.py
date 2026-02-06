import chromadb
from chromadb.config import Settings
import time
import numpy as np

# 1. 初始化具备生产级参数的本地持久化客户端
# 存储路径锁定在您的项目目录下
client = chromadb.PersistentClient(path="./amah_vector_db")

def create_optimized_collection(name):
    """
    针对 10万+ 资产的核心参数优化
    HNSW (Hierarchical Navigable Small World) 能够将检索复杂度降至 O(log N)
    """
    print(f"🚀 正在为 {name} 创建 HNSW 高速索引...")
    return client.get_or_create_collection(
        name=name,
        metadata={
            "hnsw:space": "cosine",       # 适合医疗语义余弦相似度匹配
            "hnsw:construction_ef": 200,  # 构建时搜索深度，值越高精度越高
            "hnsw:search_ef": 100,        # 检索时搜索深度，平衡速度与召回率
            "hnsw:M": 16,                 # 每个向量节点的层级连接数
            "hnsw:batch_size": 100,       # 批量写入大小
            "hnsw:sync_threshold": 1000   # 写入同步阈值
        }
    )

def load_initial_shards(collection, count=1000):
    """
    模拟批量注入资产向量条目
    在路演中，这代表了 Level 4 判定后的资产冷启动加载
    """
    print(f"📦 正在向集群注入 {count} 项资产向量条目...")
    ids = [f"asset_{i}" for i in range(count)]
    documents = [f"Medical asset node {i}: Specialized medical equipment data." for i in range(count)]
    
    # 模拟向量（实际生产中由 embedding 函数生成）
    # 确保向量维度的一致性
    embeddings = np.random.uniform(-1, 1, (count, 384)).tolist()
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents
    )

if __name__ == "__main__":
    start_time = time.time()
    
    # 执行向量分片：学科层级隔离 (Discipline Sharding)
    # 这确保了检索范围从 10万 缩减到特定学科的 2-3万
    print("--- AMAH 向量引擎初始化 ---")
    
    # 分片 1: 肿瘤/化学资产
    oncology_col = create_optimized_collection("oncology_assets")
    # 分片 2: 神经调控/DBS 资产
    neurology_col = create_optimized_collection("neurology_assets")
    
    # 加载测试数据
    load_initial_shards(neurology_col, 1000)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("-" * 40)
    print(f"✅ 索引重构完成！")
    print(f"⏱️ 初始加载耗时: {duration:.2f}s")
    print(f"💡 策略对位：Level 4 判定后，系统将秒级定位至对应 HNSW 分片。")
    print("-" * 40)
