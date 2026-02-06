# 文件名: jrct_aggregator.py
import requests
import json
import time

def fetch_japanese_assets():
    print("🇯🇵 启动日本 jRCT 专项资产抓取程序...")
    
    # 核心战略关键词：锁定日本领先的 iPS、再生医疗及神经科技
    japanese_queries = [
        "iPS cell", "regenerative medicine", "stem cell", 
        "Parkinson", "DBS", "spinal cord injury", "exosome"
    ]
    
    all_assets = []
    # 加载现有 ID 避免重复
    try:
        with open("merged_data.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            seen_ids = {item['id'] for item in existing_data}
            all_assets = existing_data
    except:
        seen_ids = set()

    session = requests.Session()
    
    # jRCT 开放搜索 API 或 镜像处理逻辑
    # 注意：jRCT ID 格式通常为 jRCTs... 或 jRCT0...
    for query in japanese_queries:
        print(f"📡 正在检索日本本土资源: [{query}]")
        
        # 使用 WHO ICTRP 接口作为中转，它是抓取 jRCT 数据最稳定的官方渠道
        url = "https://trialsearch.who.int/api/TrialSearch" 
        params = {
            "query": query,
            "recruiting": "true",
            "source": "jRCT" # 强制锁定日本注册库
        }
        
        try:
            # 此处演示逻辑，实际环境中可能需要根据 WHO 接口协议调整
            response = session.get(url, params=params, timeout=30)
            if response.status_code != 200: continue
            
            trials = response.json().get('trials', [])
            for t in trials:
                tid = t.get('TrialID')
                if tid not in seen_ids:
                    seen_ids.add(tid)
                    
                    # 映射至您的统一数据模型
                    all_assets.append({
                        "id": tid,
                        "source": "jRCT_Japan_Official",
                        "category": "Regenerative", # 日本资源多为此类
                        "title": f"【日本特色】{t.get('Public_title')}",
                        "status": "Active",
                        "criteria": t.get('Inclusion_Criteria', '') + "\n" + t.get('Exclusion_Criteria', '')
                    })
            
            print(f"✅ 已整合 {len(trials)} 项日本项目。")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ 日本节点响应异常: {e}")

    # 保存全量数据
    with open("merged_data.json", "w", encoding="utf-8") as f:
        json.dump(all_assets, f, ensure_ascii=False, indent=2)
    
    print(f"🔥 战略资产库已更新，当前规模: {len(all_assets)} 项")

if __name__ == "__main__":
    fetch_japanese_assets()
    