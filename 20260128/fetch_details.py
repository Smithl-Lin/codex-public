# 文件名: fetch_details.py
import requests
import json

def get_trial_details(nct_id):
    # 使用 ClinicalTrials.gov API v2
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None
        
    data = response.json()
    
    try:
        # 提取关键字段：标题 和 入组标准
        protocol = data.get('protocolSection', {})
        identification = protocol.get('identificationModule', {})
        eligibility = protocol.get('eligibilityModule', {})
        
        title = identification.get('officialTitle', 'No Title')
        criteria = eligibility.get('eligibilityCriteria', 'No Criteria')
        
        return f"Trial ID: {nct_id}\nTitle: {title}\n\nEligibility Criteria:\n{criteria}"
    except Exception as e:
        return f"Error parsing data: {str(e)}"

# --- 执行抓取 ---
if __name__ == "__main__":
    nct_id = "NCT04567771"  # Mayo Clinic 质子治疗试验
    full_text = get_trial_details(nct_id)
    print("--- 抓取成功，内容预览 ---")
    print(full_text[:500] + "...") # 只打印前500字符
    
    # 保存为临时文件供下一步使用
    with open("trial_data.txt", "w", encoding="utf-8") as f:
        f.write(full_text)