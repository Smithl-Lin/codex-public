# L2 医疗资产 — 继续查找纳入的要求与格式

**Stamp:** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN  
**Purpose:** 全球持续采集时，新资产需满足的字段、质量与格式，以便自动对齐内部逻辑并写入 working log。  
**Last Updated:** 2026-01-28  

---

## 1. 纳入原则

- 仅纳入**非患者个人可识别资料**：医院、临床研究（试验）、PI/专家、研究中心等。  
- 每条纳入须：符合下表格式、通过质量校验、写入对应数据源文件并记录 working log（时间、内容、纳入条目摘要）。  

---

## 2. 资产类型与纳入格式

### 2.1 临床研究（Clinical Trial / Study）

**目标文件：** merged_data.json（或 all_trials.json 作为补充源）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 唯一标识，建议 NCT 编号或官方 trial ID |
| title | string | 是 | 可选用 brief_title |
| status | string | 是 | 如 RECRUITING, COMPLETED, ACTIVE_NOT_RECRUITING；可选用 overall_status |
| criteria | string | 否 | 入选/排除标准全文或摘要 |
| source | string | 否 | 如 ClinicalTrials.gov, JRCT, EUCTR |
| category | string | 否 | 如 Oncology, Neurology, Cardiology |

**质量要求：**  
- id 不与现有 merged_data 重复。  
- title 或 category 中含以下至少一词（用于 Advanced_Therapeutic_Assets）：fda, clinical trial, cell therapy, gene therapy, stem cell, bci, brain-computer, neuro（或后续扩展标签）。  

**示例：**

```json
{
  "id": "NCT01234567",
  "title": "Phase III Trial of XYZ in NSCLC",
  "status": "RECRUITING",
  "criteria": "Inclusion: ...",
  "source": "ClinicalTrials.gov",
  "category": "Oncology"
}
```

---

### 2.2 专家 / PI（Principal Investigator）

**目标文件：** expert_map_data.json

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 唯一标识；可与 name 二选一存在 |
| name | string | 是 | 姓名或团队名 |
| affiliation | string | 是 | 机构/医院名称 |
| specialty | string | 否 | 专科 |
| expertise_tags | array of string | 否 | 如 STN-DBS, Parkinson, Phase-III |
| insurance_partners | array of string | 否 | 如 Medicare, BlueCross |
| value_add_services | array of string | 否 | 如 Travel-Concierge, Hospital-Docking |
| location | object | 否 | { "city", "state", "zip" } 或等效 |
| linked_projects | array of string | 否 | 关联的试验 id 列表 |

**质量要求：**  
- id 或 name + affiliation 组合不与现有记录重复。  
- affiliation 需为可解析的机构名（医院/大学/研究中心）。  

**示例：**

```json
{
  "id": "pi_global_001",
  "name": "Dr. Jane Doe",
  "affiliation": "Mayo Clinic, Rochester",
  "specialty": "Neuro-Oncology",
  "expertise_tags": ["Glioblastoma", "Phase-III", "Immunotherapy"],
  "insurance_partners": ["Medicare"],
  "value_add_services": ["Hospital-Docking"],
  "location": { "city": "Rochester", "state": "Minnesota", "zip": "55905" },
  "linked_projects": ["NCT01234567"]
}
```

---

### 2.3 医院 / 研究中心（Hospital / Research Center）

**目标文件：** 新建 hospital_center_assets.json，或合并入 global_elite_experts.json（精英节点）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 唯一标识 |
| name | string | 是 | 机构显示名 |
| affiliation | string | 否 | 上级机构或同义名 |
| region | string | 否 | North America, Europe, Asia-Pacific, Specialized |
| country | string | 否 | ISO 或常用国名 |
| city | string | 否 | 城市 |
| state | string | 否 | 州/省（适用时） |
| specialty_focus | array of string | 否 | 如 Oncology, Neurology |
| value_add_services | array of string | 否 | 如 International-Patient-Desk |

**质量要求：**  
- id 唯一；name 非空。  
- 非患者、非个人可识别信息。  

**示例：**

```json
{
  "id": "hosp_fl_001",
  "name": "Mayo Clinic Jacksonville",
  "affiliation": "Mayo Clinic",
  "region": "North America",
  "country": "USA",
  "city": "Jacksonville",
  "state": "Florida",
  "specialty_focus": ["Neurology", "DBS", "Movement Disorders"],
  "value_add_services": ["Travel-Concierge", "Hospital-Docking"]
}
```

---

### 2.4 区域患者覆盖（Patient Coverage by Region）— 仅聚合、去标识

**目标文件：** patient_coverage_by_region.json（置于 20260128 或 data_dir）

**纳入原则：** 仅纳入**聚合、去标识**的地区/国家覆盖量统计；**禁止任何患者个人可识别信息（PII）**。用于意图映射与 GPR 区域权重，总覆盖量可 ≥ 20 万（美国+英联邦+欧洲+大陆+香港/新加坡等）。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 唯一标识，如 cov_us_001 |
| region | string | 是 | NA / Commonwealth / EU / Asia-Pacific |
| country | string | 是 | 国家或地区名（如 United States, Hong_Kong） |
| coverage_count | number | 是 | 该地区聚合覆盖量（非个体数，可为统计/估算） |
| source_description | string | 否 | 来源说明，须注明 de-identified / No PII |

**质量要求：** id 唯一；coverage_count ≥ 0；禁止任何可识别个人的字段。

**示例：**

```json
{
  "id": "cov_us_001",
  "region": "NA",
  "country": "United States",
  "coverage_count": 85000,
  "source_description": "Aggregate de-identified coverage; US reach (illustrative). No PII."
}
```

---

## 3. 纳入流程与 Working Log

1. **校验：** 按上表检查必填、类型、唯一性。  
2. **对齐内部格式：** 脚本将外部字段映射为现有 L2 内部字段（如 id→id, title→title, affiliation→affiliation）；缺失可选字段用默认或空。  
3. **写入：**  
   - 临床研究 → 追加 merged_data.json（并可选同步 all_trials.json）；  
   - 专家/PI → 追加 expert_map_data.json；  
   - 医院/中心 → 追加 hospital_center_assets.json（或按策略合并到 global_elite_experts.json）；  
   - 区域患者覆盖 → 写入或合并 patient_coverage_by_region.json（仅聚合、禁止 PII）。  
4. **Working Log：** 每条写入一条 log，包含：  
   - **time:** ISO 8601 UTC；  
   - **action:** e.g. `ingest_trial`, `ingest_pi`, `ingest_hospital`, `ingest_patient_coverage`；  
   - **source_file:** 若来自文件；  
   - **content_summary:** 纳入条目摘要（如 id、title/name、数量）；  
   - **ids_added:** 本次纳入的 id 列表。  

Working log 文件：`asset_library_l2/working_log.jsonl`（或 `working_log.md` 按条追加）。  

---

## 4. 调用方式

- 将本目录（asset_library_l2）与 01_existing_assets.md、02_ingestion_spec.md 置于可访问路径；  
- 使用 `asset_ingest.py`（或同目录下 ingest 脚本）对单条/批量 JSON 执行纳入；  
- 采集脚本（爬虫、API 拉取等）输出符合 02 格式的 JSON 后，可直接调用 ingest 脚本，实现「持续采集 → 自动对齐格式 → 纳入资产库 → 生成 working log」。  

*End of 02_ingestion_spec*
