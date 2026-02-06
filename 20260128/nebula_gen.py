import chromadb
import json
import os
import random

def generate_nebula_json():
    print("📡 正在从 10 万级底座提取星云热力数据...")
    client = chromadb.PersistentClient(path="./amah_vector_db")
    collection = client.get_collection("expert_map_global")
    
    # 获取全部元数据
    all_data = collection.get(include=['metadatas'])
    
    nebula_points = []
    # 核心枢纽坐标参考
    hub_coords = {
        "Jacksonville": [30.3322, -81.6557],
        "Houston": [29.7604, -95.3698],
        "Boston": [42.3601, -71.0589],
        "Cleveland": [41.4993, -81.6944],
        "Baltimore": [39.2904, -76.6122]
    }
    
    total = len(all_data['ids'])
    for i in range(total):
        meta = all_data['metadatas'][i]
        city = meta.get('hub', 'Jacksonville')
        base_coords = hub_coords.get(city, [30.3322, -81.6557])
        
        # 加入随机扰动使热力图分布更自然
        lat = base_coords[0] + random.uniform(-1.5, 1.5)
        lng = base_coords[1] + random.uniform(-1.5, 1.5)
        
        point = {
            "id": all_data['ids'][i],
            "lat": round(lat, 4),
            "lng": round(lng, 4),
            "val": random.uniform(0.4, 1.0), # 模拟权重
            "domain": meta.get('specialty', 'Neurology')
        }
        nebula_points.append(point)
        
        if i % 25000 == 0:
            print(f"✅ 进度: {i}/{total}")

    with open('nebula_data.json', 'w') as f:
        json.dump(nebula_points, f)
    
    print(f"\n✨ 数据包生成完毕: nebula_data.json (共 {total} 个节点)")

if __name__ == "__main__":
    generate_nebula_json()
