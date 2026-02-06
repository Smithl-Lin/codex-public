# 文件名: monitor_status.py
import requests
import json
import time
import os
from datetime import datetime

# 模拟发送邮件/通知的函数
def send_alert(trial_id, old_status, new_status, title):
    print("\n" + "!"*40)
    print(f"🚨 警报：试验状态变更检测！")
    print(f"🆔 试验 ID: {trial_id}")
    print(f"📄 标题: {title[:50]}...")
    print(f"❌ 旧状态: {old_status}")
    print(f"✅ 新状态: {new_status}")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("!"*40 + "\n")
    # 在真实场景中，这里会调用 SMTP 发送邮件或 Twilio 发送短信

def check_updates():
    # 1. 读取本地数据库 (基准数据)
    if not os.path.exists("all_trials.json"):
        print("请先运行 batch_fetch.py 生成本地数据。")
        return

    with open("all_trials.json", "r", encoding="utf-8") as f:
        local_trials = json.load(f)

    print(f"🔍 开始巡检 {len(local_trials)} 个试验的实时状态...\n")

    updates_found = False

    # 2. 遍历每一个试验，去 API 查最新状态
    for trial in local_trials:
        nct_id = trial['id']
        local_status = trial.get('status', 'Unknown')
        
        # 请求 API
        url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}?fields=StatusModule"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                remote_data = response.json()
                remote_status = remote_data.get('protocolSection', {}).get('statusModule', {}).get('overallStatus', 'Unknown')
                
                # 3. 核心逻辑：比对状态
                if remote_status != local_status:
                    send_alert(nct_id, local_status, remote_status, trial['title'])
                    # 更新内存中的数据
                    trial['status'] = remote_status
                    updates_found = True
                else:
                    print(f"✅ {nct_id}: 状态未变 ({local_status})")
            else:
                print(f"⚠️ 无法获取 {nct_id}: HTTP {response.status_code}")
        
        except Exception as e:
            print(f"❌ 网络错误 {nct_id}: {e}")
        
        time.sleep(0.5) # 避免 API 速率限制

    # 4. 如果有更新，回写到本地文件
    if updates_found:
        print("💾 检测到更新，正在同步至本地数据库...")
        with open("all_trials.json", "w", encoding="utf-8") as f:
            json.dump(local_trials, f, ensure_ascii=False, indent=2)
    else:
        print("\n✨ 巡检结束，所有试验状态正常。")

if __name__ == "__main__":
    check_updates()