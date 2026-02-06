# 文件名: fda_device_fetch.py
import requests
import json
from datetime import datetime, timedelta

def fetch_recent_devices(limit=5):
    """
    从 OpenFDA 获取最近获批的高端医疗器械 (PMA)
    """
    # 获取过去 1 年的数据
    last_year = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    base_url = "https://api.fda.gov/device/pma.json"
    query = f"decision_date:[{last_year} TO 2026-12-31]"
    
    params = {
        "search": query,
        "limit": limit
    }
    
    print(f"⚙️ 正在扫描 FDA 数据库 (PMA Devices)...")
    try:
        response = requests.get(base_url, params=params, timeout=10)
        data = response.json()
        
        cleaned_data = []
        for device in data.get('results', []):
            # FDA 数据没有 NCT ID，我们生成一个唯一的 FDA ID
            fda_id =f"FDA_{device.get('pma_number')}"
            
            cleaned_data.append({
                "id": fda_id,
                "source": "FDA_PMA",
                "title": f"【FDA获批器械】{device.get('trade_name')} ({device.get('applicant')})",
                "status": "Approved",
                "criteria": f"Device Generic Name: {device.get('generic_name')}\n"
                            f"Approval Date: {device.get('decision_date')}\n"
                            f"Description: 此设备已通过 FDA PMA 最严苛审批，可用于临床治疗。"
            })
        return cleaned_data
    except Exception as e:
        print(f"FDA Fetch Error: {e}")
        return []

if __name__ == "__main__":
    data = fetch_recent_devices(3)
    print(json.dumps(data, indent=2, ensure_ascii=False))