# L2 医疗资产库 — 采集与纳入

**Stamp:** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN  
**Purpose:** 随时调用、持续采集全球医疗资产（医院、临床研究、PI）并纳入资产库；自动对齐内部格式并生成 working log。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| **01_existing_assets.md** | 已有资产：数量、质量要求、格式、数据源与代码引用 |
| **02_ingestion_spec.md** | 继续查找纳入的要求与格式（临床研究 / PI / 医院） |
| **asset_ingest.py** | 纳入脚本：校验 → 对齐格式 → 写入对应 JSON → 写入 working log |
| **working_log.jsonl** | 纳入日志（机器可读，每行一条 JSON） |
| **working_log.md** | 纳入日志（人可读表格：时间、内容、纳入的 id） |
| **top100_hospitals_data.json** | 全球前100医院数据（Newsweek/Statista 2025 + 扩展）；供 ingest_top100_hospitals 使用 |

---

## 全球前100医院一次性纳入

从 **20260128** 目录执行：

```bash
python ingest_top100_hospitals.py
```

将纳入：100 家医院（hosp_top_001..100）、100 个 Lead Clinical Team（pi_top_001..100）、80 条代表临床研究（NCT_TOP_0001..0080）。数据来源见 `top100_hospitals_data.json`。纳入后请执行 `python sync_l2_to_chromadb.py` 更新物理节点注册表。

---

## 调用方式

### 1. 命令行（单次或批量文件）

```bash
# 从 20260128 目录执行
cd 20260128
python asset_library_l2/asset_ingest.py trial   path/to/new_trials.json
python asset_library_l2/asset_ingest.py pi       path/to/new_pis.json
python asset_library_l2/asset_ingest.py hospital path/to/new_hospitals.json
```

### 2. Python 调用（嵌入采集流水线）

```python
import sys
sys.path.insert(0, "20260128")
from asset_library_l2.asset_ingest import ingest

# 临床研究
count, ids = ingest("trial", [{"id": "NCT09999999", "title": "...", "status": "RECRUITING", ...}])

# 专家/PI
count, ids = ingest("pi", [{"id": "pi_001", "name": "Dr. X", "affiliation": "Mayo Clinic", ...}])

# 医院/中心
count, ids = ingest("hospital", [{"id": "hosp_001", "name": "XYZ Hospital", ...}])
```

采集脚本只需输出符合 **02_ingestion_spec.md** 的 JSON，再调用 `ingest()` 即可自动对齐格式、写入资产文件并记录 working log（时间、内容、纳入的 id）。

---

## Working Log 字段

每条记录包含：

- **time:** ISO 8601 UTC  
- **action:** ingest_trial | ingest_pi | ingest_hospital  
- **content_summary:** 摘要（如 "trials added: 5"）  
- **ids_added:** 本次纳入的 id 列表  
- **count:** 本次纳入条数  
- **source_file:** 可选，来源文件路径  

*End of README*
