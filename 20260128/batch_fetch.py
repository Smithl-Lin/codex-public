# 文件名: batch_fetch.py
import requests
import json
import time

def fetch_trial_data(nct_id):
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # 提取核心字段
            protocol = data.get('protocolSection', {})
            ident = protocol.get('identificationModule', {})
            eligibility = protocol.get('eligibilityModule', {})
            
            return {
                "id": nct_id,
                "title": ident.get('officialTitle', 'No Title'),
                "criteria": eligibility.get('eligibilityCriteria', 'No Criteria'),
                "status": protocol.get('statusModule', {}).get('overallStatus', 'Unknown')
            }
        else:
            print(f"⚠️ {nct_id} 下载失败: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ {nct_id} 发生错误: {e}")
        return None

# --- 主程序 ---
if __name__ == "__main__":
    results = []
    
    # 1. 读取目标列表
    with open("target_trials.txt", "r") as f:
        # 过滤空行，去除换行符
        ids = [line.strip() for line in f if line.strip()]
    
    print(f"开始批量抓取 {len(ids)} 个试验...")
    
    # 2. 循环抓取
    for nct_id in ids:
        print(f"📥 正在抓取: {nct_id} ...")
        data = fetch_trial_data(nct_id)
        if data:
            results.append(data)
        time.sleep(1) # 礼貌延时，防止被封 IP
        
    # 3. 保存为 JSON
    with open("all_trials.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"\n✅ 批量抓取完成！已保存 {len(results)} 条数据到 'all_trials.json'")