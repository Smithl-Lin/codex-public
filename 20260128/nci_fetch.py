# 文件名: nci_fetch.py
import requests
import json

def fetch_nci_trials(keyword="lung cancer", limit=5):
    """
    从美国国家癌症研究所 (NCI) 获取结构化数据
    优势：包含更详细的 Biomarkers 和 NCI 官方分类
    """
    base_url = "https://clinicaltrialsapi.cancer.gov/v1/clinical-trials"
    
    params = {
        "current_trial_status": "Active", # 只看活跃的
        "keyword": keyword,
        "size": limit,
        "include": ["nct_id", "brief_title", "official_title", "brief_summary", "biomarkers", "sites"]
    }
    
    print(f"🎗️ 正在连接 NCI 数据库搜索: {keyword}...")
    try:
        response = requests.get(base_url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            trials = data.get('trials', [])
            
            cleaned_data = []
            for t in trials:
                # 提取高价值的生物标志物信息 (Precision Medicine)
                bios = [b.get('name') for b in t.get('biomarkers', []) if b.get('name')]
                bio_str = ", ".join(bios) if bios else "无特定靶点限制"
                
                cleaned_data.append({
                    "id": t['nct_id'],
                    "source": "NCI_API",
                    "title": t['brief_title'],
                    "status": "Active",
                    # 将生物标志物强行注入到 Criteria 中，方便向量检索
                    "criteria": f"【NCI Precision Data】\nTarget Biomarkers: {bio_str}\n\nSummary:\n{t['brief_summary']}"
                })
            return cleaned_data
        else:
            print(f"NCI API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"NCI Connection Failed: {e}")
        return []

if __name__ == "__main__":
    # 测试抓取
    data = fetch_nci_trials("pancreatic cancer", 3)
    print(json.dumps(data, indent=2, ensure_ascii=False))