import time
from Bio import Entrez
import json
import os

# ================= 配置区 =================
Entrez.email = "smithlin_demo@google.com"  # 保持您的邮箱设置
OUTPUT_DIR = "AMANI_Training_Data"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ================= 饱和式搜索策略 =================
# 逻辑升级：SEARCH_POOL 设定为 5000，确保即使损耗率高，也能凑满 target_count
TARGETS = [
    {
        "category": "Neuro_Degenerative",
        "target_count": 500, # 必须凑满的数量
        "search_pool": 5000, # 搜索池深度
        "term": '("Multiple System Atrophy" OR "Amyotrophic Lateral Sclerosis" OR "Parkinson Disease" OR "Alzheimer Disease" OR "Progressive Supranuclear Palsy" OR "Dementia") AND "Case Reports"[pt] AND English[lang]'
    },
    {
        "category": "Oncology_Complex",
        "target_count": 300,
        "search_pool": 3000,
        "term": '("Brain Neoplasms" OR "Lung Neoplasms" OR "Liver Neoplasms" OR "Pancreatic Neoplasms" OR "Mutation") AND "Case Reports"[pt] AND English[lang]'
    },
    {
        "category": "Rare_Undiagnosed",
        "target_count": 200,
        "search_pool": 2000,
        "term": '("Rare Diseases" OR "Undiagnosed Diseases" OR "Diagnostic Errors") AND "Case Reports"[pt] AND English[lang]'
    },
    {
        "category": "Pediatric_Developmental",
        "target_count": 200,
        "search_pool": 2000,
        "term": '("Infant" OR "Child" OR "Developmental Disabilities" OR "Genetic Diseases, Inborn") AND "Case Reports"[pt] AND English[lang]'
    }
]

# ================= 功能函数 =================

def search_cases(term, max_ret_count):
    """获取大量 ID 作为矿池"""
    try:
        # 使用 sort='date' 获取最新的病例，质量通常更高
        handle = Entrez.esearch(db="pubmed", term=term, retmax=max_ret_count, sort="date")
        record = Entrez.read(handle)
        handle.close()
        return record["IdList"]
    except Exception as e:
        print(f"    [!] Search Error: {e}")
        return []

def fetch_and_filter(id_pool, target_needed, batch_size=50):
    """
    饱和式下载：直到凑满 target_needed 为止
    """
    valid_articles = []
    total_scanned = 0
    
    # 循环处理矿池中的 ID
    for i in range(0, len(id_pool), batch_size):
        # 检查是否已经凑够了
        if len(valid_articles) >= target_needed:
            break
            
        batch_ids = id_pool[i:i+batch_size]
        try:
            print(f"    -> Scanning batch {i}/{len(id_pool)} | Valid collected: {len(valid_articles)}/{target_needed}...")
            handle = Entrez.efetch(db="pubmed", id=batch_ids, retmode="xml")
            records = Entrez.read(handle)
            handle.close()
            
            if 'PubmedArticle' in records:
                for article in records['PubmedArticle']:
                    # 如果已经够了，直接退出内层循环
                    if len(valid_articles) >= target_needed:
                        break
                        
                    try:
                        medline = article['MedlineCitation']
                        article_data = article['MedlineCitation']['Article']
                        
                        # 严格过滤：必须有非空的摘要
                        if 'Abstract' not in article_data or 'AbstractText' not in article_data['Abstract']:
                            continue
                            
                        abstract_text = article_data['Abstract']['AbstractText']
                        final_abstract = " ".join([str(x) for x in abstract_text]) if isinstance(abstract_text, list) else str(abstract_text)
                        
                        # 二次过滤：摘要长度太短的不要（往往是无效信息）
                        if len(final_abstract) < 50:
                            continue

                        data = {
                            "pmid": str(medline['PMID']),
                            "title": article_data.get('ArticleTitle', ''),
                            "abstract": final_abstract,
                            "keywords": [str(kw) for kw in medline.get('KeywordList', [[]])[0]] if 'KeywordList' in medline else [],
                            "date": article_data.get('ArticleDate', [{}])[0].get('Year', '')
                        }
                        valid_articles.append(data)
                        
                    except Exception:
                        continue
            
            time.sleep(0.5) # 避免过快
            
        except Exception as e:
            print(f"    [!] Batch Error: {e}")
            continue

    return valid_articles

# ================= 主程序 =================

def main():
    print("=== A.M.A.N.I. Data Miner V1.3 (Saturation Mode) ===")
    print("Strategy: Over-fetch IDs to guarantee target count.")
    print("---------------------------------------------")

    total_collected = 0

    for target in TARGETS:
        category = target["category"]
        goal = target["target_count"]
        print(f"\n>>> Starting Job: {category} (Target: {goal})")
        
        # 1. 建立巨大的 ID 矿池
        id_pool = search_cases(target["term"], target["search_pool"])
        print(f"    -> ID Pool created with {len(id_pool)} candidates.")
        
        if id_pool:
            # 2. 饱和式下载
            data = fetch_and_filter(id_pool, goal)
            
            # 3. 保存
            if data:
                filename = os.path.join(OUTPUT_DIR, f"{category}_training_set.json")
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                print(f"✅ SUCCESS: Collected {len(data)}/{goal} cases for {category}")
                total_collected += len(data)
            else:
                print(f"⚠️ Warning: Scanned all IDs but found 0 valid abstracts.")
        else:
            print(f"⚠️ Error: Search returned 0 IDs.")

    print("\n=============================================")
    print(f"🚀 Mission Complete. Total High-Quality Cases: {total_collected}")
    print(f"📁 Data location: {os.path.abspath(OUTPUT_DIR)}")
    print("=============================================")

if __name__ == "__main__":
    main()