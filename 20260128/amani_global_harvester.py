# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# ==========================================
# 🌍 A.M.A.N.I. Global Data Harvester (100K+ Edition) V4.0 — AGID 输出体系
# ==========================================
import pandas as pd
import time
import os
import logging
import hashlib
import datetime

try:
    from Bio import Entrez
    Entrez.email = "amani_global_strategy@google_demo.com"
except Exception:
    Entrez = None

TARGET_COUNT = 100000
BATCH_SIZE = 500
MAX_WORKERS = 10
OUTPUT_FILE = "AMANI_GLOBAL_100K_RAW.csv"
SEARCH_TERM = '("Case Reports"[Publication Type] OR "Clinical Trial"[Publication Type]) AND ("2015"[Date - Publication] : "2026"[Date - Publication])'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# AGID 体系
# ------------------------------------------------------------------------------
def to_agid(namespace: str, node_type: str, raw_id) -> str:
    sid = hashlib.sha256(f"{namespace}:{node_type}:{raw_id}".encode()).hexdigest()[:12].upper()
    return f"AGID-{namespace}-{node_type}-{sid}"


def fetch_details(id_list):
    if Entrez is None:
        return []
    try:
        handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
        records = Entrez.read(handle)
        handle.close()
        batch_data = []
        for article in records['PubmedArticle']:
            try:
                citation = article['MedlineCitation']
                pmid = citation['PMID']
                article_data = citation['Article']
                title = article_data.get('ArticleTitle', 'No Title')
                if 'Abstract' in article_data:
                    abstract_parts = article_data['Abstract']['AbstractText']
                    abstract_text = " ".join(abstract_parts) if isinstance(abstract_parts, list) else str(abstract_parts)
                else:
                    continue
                keywords = []
                if 'MeshHeadingList' in citation:
                    for mesh in citation['MeshHeadingList']:
                        keywords.append(str(mesh['DescriptorName']))
                # V4.0: 每条记录输出 AGID
                agid = to_agid("HARV", "RECORD", str(pmid))
                batch_data.append({
                    "agid": agid,
                    "PMID": str(pmid),
                    "Title": title,
                    "Abstract": abstract_text,
                    "Keywords": "; ".join(keywords[:5]),
                    "Region": "Global_Public_Source",
                    "Fetch_Time": datetime.datetime.now().strftime('%Y-%m-%d')
                })
            except Exception:
                continue
        return batch_data
    except Exception:
        return []


def run_mega_harvest():
    print(f"🚀 A.M.A.N.I. 全球数据收割机 V4.0 启动 | 目标: {TARGET_COUNT} 例 | AGID 输出")
    if Entrez is None:
        print("❌ Bio.Entrez 未安装，跳过网络拉取。")
        return
    print("🔍 正在检索全球索引...")
    try:
        handle = Entrez.esearch(db="pubmed", term=SEARCH_TERM, retmax=TARGET_COUNT, retmode="xml")
        record = Entrez.read(handle)
        handle.close()
        id_list = record["IdList"]
        print(f"✅ 成功锁定 {len(id_list)} 份病例档案。准备开始并发下载...")
    except Exception as e:
        print(f"❌ 索引检索失败: {e}")
        return

    try:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from tqdm import tqdm
    except ImportError:
        ThreadPoolExecutor = None
    all_data = []
    batches = [id_list[i:i + BATCH_SIZE] for i in range(0, len(id_list), BATCH_SIZE)]
    if ThreadPoolExecutor:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_batch = {executor.submit(fetch_details, b): b for b in batches}
            for future in tqdm(as_completed(future_to_batch), total=len(batches), desc="Downloading Global Data"):
                result = future.result()
                if result:
                    all_data.extend(result)
                if len(all_data) >= 5000:
                    save_chunk(all_data)
                    all_data = []
    else:
        for batch in batches:
            all_data.extend(fetch_details(batch))
            if len(all_data) >= 5000:
                save_chunk(all_data)
                all_data = []
    if all_data:
        save_chunk(all_data)
    print(f"\n🏆 任务结束！数据已保存至: {OUTPUT_FILE} (V4.0 AGID)")


def save_chunk(data):
    df = pd.DataFrame(data)
    if not os.path.isfile(OUTPUT_FILE):
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(OUTPUT_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
    logger.info(f"💾 已归档 {len(data)} 条数据 (AGID)...")


if __name__ == "__main__":
    run_mega_harvest()
