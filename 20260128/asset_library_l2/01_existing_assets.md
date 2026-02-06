# L2 医疗资产 — 已有资产清单

**Stamp:** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN  
**Scope:** 非患者资料；医院、临床研究、PI（Principal Investigator）等 L2 医疗资产。  
**Last Updated:** 2026-01-28（已纳入全球前100医院 + 每院 Lead Clinical Team + 代表临床研究 80 条）  

---

## 1. 资产类型与数量

| 资产类型 | 数据源文件 | 当前数量 | 存储/索引 |
|----------|------------|----------|-----------|
| **临床研究（试验）** | merged_data.json | 19,361+ | ChromaDB: mayo_clinic_trials；L2 Component_2: Advanced_Therapeutic_Assets；含全球前100医院代表试验 80 条（NCT_TOP_*） |
| **临床研究（补充）** | all_trials.json | 3 | 与 merged_data 合并使用 |
| **专家/PI** | expert_map_data.json | 150 | L2 Component_3: Principal_Investigator_Registry；ChromaDB: expert_map_global；含前100医院 Lead Clinical Team 100 条（pi_top_001..100） |
| **精英中心/团队** | global_elite_experts.json | 4 | 顶级医院/中心节点 |
| **医院/中心** | hospital_center_assets.json | 117 | 全球前100医院（hosp_top_001..100，Newsweek/Statista 2025 + 扩展）；历史 17 条 |

| **区域患者覆盖（聚合）** | patient_coverage_by_region.json | 多地区条，总计数 ≥ 20 万 | 仅聚合、去标识（美国+英联邦+欧洲+大陆+香港新加坡）；供 GPR/意图映射；禁止 PII |
| **主诉均等化（L2）** | cultural_complaint_mapping.json + amani_cultural_equalizer_l2.py | 配置 + 模块 | 不同文化背景主诉 → 平权文本；供 StaircaseMappingLLM/MedicalReasoner 前均等化；见 03_cultural_main_complaint_equalizer.md |
| **硬锚点布尔拦截（L2/L3）** | amah_config.hard_anchor_boolean_interception + amani_trinity_bridge | 配置 + 逻辑 | 原子级技术词（iPS, BCI, KRAS G12C 等）识别；百级检索池 N=100 二次重排防降级匹配；见 04_hard_anchor_boolean_interception.md |
| **客户需求/训练数据模版** | amani_training_10k.json + generate_high_end_data.py | 10,000 条 | 高端主诉合成数据（request_id, original_inquiry, standard_mapping, asset_category, l1_entropy_target）；BCI/基因治疗/干细胞/临床研究四类均分；见 05_customer_demand_training_template.md |

**合计（可计数）：** 临床研究 19,364+ 条（去重后以 merged 为准）、专家/PI 150 条、精英中心 4 条、医院/中心 117 条；区域患者覆盖为聚合统计（总计数 ≥ 20 万）。物理节点注册表 physical_node_registry.json 267 条（由 sync_l2_to_chromadb 从 expert_map + hospital_center 生成）。

---

## 2. 质量要求（当前逻辑）

- **临床研究：**  
  - 纳入 Advanced_Therapeutic_Assets 需通过 `_is_therapeutic_asset()`：title/category 含 fda、clinical trial、cell therapy、gene therapy、stem cell、bci、brain-computer、neuro 等标签。  
  - 去重：以 `id`（或 nct_id）为唯一键；batch_build_db 以 id 去重后注入 ChromaDB。  
- **专家/PI：**  
  - 需具备 id/name、affiliation；可选 linked_projects、specialty、expertise_tags、location。  
  - 纳入后自动分配 AGID（PI-REGISTRY）。  
- **精英中心：**  
  - 结构需含 id、name、affiliation、specialty、expertise_tags、insurance_partners、value_add_services、location。  

---

## 3. 格式规范（已有）

### 3.1 临床研究（merged_data.json / all_trials.json）

```json
{
  "id": "NCT02465060",
  "source": "ClinicalTrials.gov",
  "category": "Oncology",
  "title": "Molecular Analysis for Therapy Choice (MATCH)",
  "status": "RECRUITING",
  "criteria": "Inclusion Criteria: ..."
}
```

**必填：** id（或 nct_id）、title（或 brief_title）、status（或 overall_status）。  
**可选：** source、category、criteria。

### 3.2 专家/PI（expert_map_data.json → Principal_Investigator_Registry）

```json
{
  "id": "exp_jax_001_v3",
  "name": "Dr. Smith (Mayo JAX)",
  "affiliation": "Mayo Clinic Jacksonville Florida",
  "specialty": "Neuromodulation",
  "expertise_tags": ["STN-DBS", "Parkinson", "Florida"],
  "insurance_partners": ["Medicare", "BlueCross"],
  "value_add_services": ["Travel-Concierge", "Hospital-Docking"],
  "location": { "city": "Jacksonville", "state": "Florida", "zip": "32224" },
  "linked_projects": []
}
```

**必填：** id 或 name、affiliation。  
**可选：** agid、linked_projects、specialty、expertise_tags、insurance_partners、value_add_services、location。

### 3.3 精英中心/医院（global_elite_experts.json）

与专家格式兼容，侧重 affiliation 为机构名；含 id、name、affiliation、specialty、expertise_tags、insurance_partners、value_add_services、location。

---

## 4. 代码引用位置

- **L2 组件定义：** amah_centurion_injection.py  
  - Global_Patient_Resources → merged_data.json（按区域索引，非患者个人资料）  
  - Advanced_Therapeutic_Assets → merged_data.json, all_trials.json  
  - Principal_Investigator_Registry → expert_map_data.json  
- **ChromaDB：**  
  - mayo_clinic_trials ← batch_build_db.py（ids, documents=criteria, metadatas=source/category/title/status）  
  - expert_map_global ← expert_bulk_loader.py, amah_nebula_injection.py 等  
- **全球医院枢纽列表：** global_expert_expansion_v2.py 内 global_medical_hubs（North America / Europe / Asia-Pacific / Specialized）。  

---

## 5. 说明

- 患者个人资料不纳入本资产库；merged_data 中的「患者」指试验入选标准描述，非可识别患者数据。  
- 医院/中心：新采集资产写入 hospital_center_assets.json（由 asset_ingest.py 首次纳入时创建）；纳入脚本自动对齐格式并记录 working log。  

---

## 6. 患者资料与 GPR 说明（系统设计 vs 遗漏）

- **患者个人可识别资料（PII）：** 为**系统设计不纳入**，非遗漏。合规要求：仅纳入非患者个人可识别资料（见 02_ingestion_spec 纳入原则）。  
- **Global_Patient_Resources（GPR）：** 数据来源为 merged_data.json（临床试验列表），按区域（NA / Commonwealth / EU / Asia-Pacific）索引；每条记录为试验 id/agid/region/category/title/status，**非**患者个体表。用于意图映射与区域对齐，不包含任何患者 PII。  
- **区域患者覆盖（新增）：** 为满足「患者数量 20w+」的覆盖量表述，新增资产类型 **区域患者覆盖**（patient_coverage_by_region）：**仅聚合、去标识**的按地区/国家统计（如覆盖人数、可服务人群量），禁止任何个人可识别信息；总计数 ≥ 20 万。数据来源为公开或合规的聚合统计（美国 + 英联邦 + 欧洲 + 大陆 + 香港/新加坡）。  

*End of 01_existing_assets*
