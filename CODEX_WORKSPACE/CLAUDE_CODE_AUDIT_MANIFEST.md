# Claude Code 审核项目 — 调用清单与目录信息

**用途：** 供 Claude Code（或同类工具）调用、审核 A.M.A.N.I. 项目时，作为「所有文件信息 + 目录」的单一入口。  
**项目根：** `AMANI Project/`（工作区根）  
**代码与资产主目录：** `20260128/`  
**Stamp：** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN  

---

## 一、目录结构（树形）

```
AMANI Project/
└── 20260128/                          # 主工作目录（L1–L4 代码 + 资产 + 配置）
    ├── .env                            # 环境变量（勿提交）
    ├── .env.example                    # 环境变量模板
    ├── .gitignore
    ├── .Rhistory
    ├── amah_config.json                # 项目统一配置
    ├── config.py                       # 凭证与配置加载
    │
    ├── app.py                          # Streamlit 主入口
    ├── app_v4.py                       # V4 闭环 UI
    │
    ├── amani_trinity_bridge.py         # Trinity 统一入口（L1→L2.5→L3→L4）
    ├── amani_core_v4.py                # L1 规则与协议
    ├── amani_nexus_layer_v3.py         # L3 NexusRouter / ComplianceGate
    ├── amani_interface_layer_v4.py    # L4 UIPresenter / 批处理接口
    ├── amani_value_layer_v4.py         # L2.5 价值编排
    ├── amani_global_nexus_v4.py        # L3 GlobalNexus
    ├── amah_centurion_injection.py     # L2 四组件与 Centurion 调度
    ├── amani_cultural_equalizer_l2.py  # L2 主诉均等化
    ├── medical_reasoner.py            # MedicalReasoner / Orchestrator / BatchProcessQueue
    │
    ├── amani_brain.py / amani_brain_v4.py
    ├── amah_weight_orchestrator.py
    ├── billing_engine.py
    ├── trinity_api_connector.py
    ├── conflict_governance_v2_5.py
    ├── consensus_lock.py
    │
    ├── sync_l2_to_chromadb.py          # 生成 physical_node_registry 并注册
    ├── batch_build_db.py               # merged_data → ChromaDB
    ├── asset_audit_final.py
    ├── sovereignty_integrity_check.py
    ├── run_trinity_oncology_case.py
    ├── test_amani_v4_full_loop.py
    ├── check_v4_baseline.py
    │
    ├── expert_bulk_loader.py
    ├── expert_data_generator.py
    ├── amah_mega_loader.py
    ├── amah_nebula_injection.py
    ├── blitz_expansion.py / blitz_expansion_v2.py
    ├── global_expert_expansion_v2.py
    │
    ├── batch_fetch.py / fetch_details.py
    ├── nci_fetch.py
    ├── jrct_aggregator.py
    ├── frontier_special_aggregator.py
    ├── fda_device_fetch.py
    ├── monitor_status.py
    │
    ├── forensic_debug.py / debug_api.py
    ├── data_synthesizer.py
    ├── check_models.py
    ├── gemini_diag.py
    ├── data_purifier.py
    ├── amani_data_miner.py
    ├── calibration_engine.py
    ├── ontology_engine.py
    ├── medical_kg.py
    ├── wellness_asset_injector.py
    ├── ingest_top100_hospitals.py
    │
    ├── expert_map_data.json
    ├── hospital_center_assets.json
    ├── merged_data.json
    ├── merged_data_cleaned.json
    ├── all_trials.json
    ├── global_elite_experts.json
    ├── physical_node_registry.json
    ├── patient_coverage_by_region.json
    ├── nebula_data.json
    ├── precision_kg.json
    ├── amani_finetuning_dataset.jsonl
    ├── global_medical_assets.csv
    │
    ├── CURSOR_AMANI_WORK_SUMMARY.md
    ├── SYSTEM_AUDIT_REPORT_AMANI.md
    ├── MEDICAL_REASONER_ORCHESTRATOR_EVALUATION.md
    ├── FEASIBILITY_REVIEW_FOUR_PHASES.md
    ├── TRINITY_ONCOLOGY_RUN_LOG.md
    ├── WORK_LOG_TRINITY_V4_20260128.md
    ├── CLAUDE_CODE_AUDIT_MANIFEST.md    # 本文件
    │
    └── asset_library_l2/                 # L2 资产库（配置 + 数据 + 纳入脚本）
        ├── 01_existing_assets.md         # 已有资产清单
        ├── 02_ingestion_spec.md          # 纳入规范
        ├── 03_cultural_main_complaint_equalizer.md  # 主诉均等化说明
        ├── README.md
        ├── asset_ingest.py               # 资产纳入入口
        ├── ingest_csv_assets.py
        ├── load_0131global_medical_assets.py
        ├── cultural_complaint_mapping.json
        ├── top100_hospitals_data.json
        ├── sample_hospitals.json
        ├── new_assets_20260202.csv
        ├── working_log.jsonl
        ├── working_log.md
        ├── 0131global_medical_assets
        └── 继续使用Python查找医疗资产的具体要求.txt
```

---

## 二、按类型与层级 — 所有文件路径与职责

### 2.1 配置与凭证

| 相对路径 | 职责 |
|----------|------|
| 20260128/config.py | 统一加载 GEMINI/OPENAI/ANTHROPIC/GOOGLE_APPLICATION_CREDENTIALS/MEDGEMMA 等 |
| 20260128/amah_config.json | precision_lock、trinity_audit_gate、medgemma、orchestrator_audit、weight_hardening |
| 20260128/.env.example | 环境变量模板（复制为 .env 使用） |
| 20260128/.gitignore | 排除 .env、*.pem、google_key.json 等 |

### 2.2 主入口与 L1–L4 核心

| 相对路径 | 层级/职责 |
|----------|-----------|
| 20260128/app.py | Streamlit 主入口；TrinityBridge.run_safe；L4 展示 |
| 20260128/app_v4.py | V4 闭环；阈值来自 core + config |
| 20260128/amani_trinity_bridge.py | Trinity 单入口；ECNNSentinel、StaircaseMappingLLM、GNNAssetAnchor、均等化、UIPresenter |
| 20260128/amani_core_v4.py | L1 规则；D≤0.79、方差门控、AGID、StrategicInterceptError |
| 20260128/amani_nexus_layer_v3.py | L3 NexusRouter.auto_register、ComplianceGate |
| 20260128/amani_interface_layer_v4.py | L4 UIPresenter；enqueue_image_for_batch、get_batch_job_status |
| 20260128/amani_value_layer_v4.py | L2.5 AMAHValueOrchestrator、Shadow Quote、billing matrix |
| 20260128/amani_global_nexus_v4.py | L3 GlobalNexus.dispatch |
| 20260128/amah_centurion_injection.py | L2 四组件；AMAHCenturionInjector.get_latest_snapshot |
| 20260128/amani_cultural_equalizer_l2.py | L2 主诉均等化 equalize_main_complaint |
| 20260128/medical_reasoner.py | MedicalReasoner、Orchestrator 主权审计、BatchProcessQueue |

### 2.3 脑模型、计费、API、治理

| 相对路径 | 职责 |
|----------|------|
| 20260128/amani_brain.py | Trinity 主脑、E-CNN、AGID、权重 |
| 20260128/amani_brain_v4.py | V4 脑模型 |
| 20260128/amah_weight_orchestrator.py | 权重编排与熵 |
| 20260128/billing_engine.py | D≤0.79 计费、AGID 报价 |
| 20260128/trinity_api_connector.py | Gemini/Claude/GPT 加权共识 |
| 20260128/conflict_governance_v2_5.py | 冲突治理 |
| 20260128/consensus_lock.py | 共识锁定 |

### 2.4 资产与 ChromaDB 同步

| 相对路径 | 职责 |
|----------|------|
| 20260128/sync_l2_to_chromadb.py | 生成 physical_node_registry.json 并 NexusRouter.auto_register |
| 20260128/batch_build_db.py | merged_data.json → ChromaDB mayo_clinic_trials |
| 20260128/expert_bulk_loader.py | 专家注入 ChromaDB |
| 20260128/expert_data_generator.py | 专家数据生成 |
| 20260128/amah_mega_loader.py | 资产加载 |
| 20260128/amah_nebula_injection.py | Nebula 注入 |
| 20260128/blitz_expansion.py / blitz_expansion_v2.py | 资产扩展 |
| 20260128/global_expert_expansion_v2.py | 全球专家扩展 |
| 20260128/ingest_top100_hospitals.py | 前 100 医院纳入 |

### 2.5 外部 API 与爬虫

| 相对路径 | 职责 |
|----------|------|
| 20260128/batch_fetch.py | ClinicalTrials.gov API |
| 20260128/fetch_details.py | 试验详情拉取 |
| 20260128/nci_fetch.py | NCI API |
| 20260128/jrct_aggregator.py | WHO TrialSearch 等 |
| 20260128/frontier_special_aggregator.py | 前哨试验聚合 |
| 20260128/fda_device_fetch.py | FDA device API |
| 20260128/monitor_status.py | 试验状态巡检 |

### 2.6 诊断、调试、数据合成

| 相对路径 | 职责 |
|----------|------|
| 20260128/forensic_debug.py | 调试（使用 config.get_gemini_api_key） |
| 20260128/debug_api.py | API 调试 |
| 20260128/data_synthesizer.py | 数据合成 |
| 20260128/check_models.py | 模型检查 |
| 20260128/gemini_diag.py | Gemini 诊断（使用 config 凭证路径） |
| 20260128/data_purifier.py | 清洗与 AGID 输出 |
| 20260128/amani_data_miner.py | PubMed 等采集 |
| 20260128/calibration_engine.py | 应力数据集、波形拦截 |

### 2.7 其他脚本与工具

| 相对路径 | 职责 |
|----------|------|
| 20260128/advanced_aggregator.py | 聚合与 0.79 闭环 |
| 20260128/auto_sync.py | 交付端数据粘合 |
| 20260128/ontology_engine.py | 本体 |
| 20260128/medical_kg.py | 医学知识图谱 |
| 20260128/wellness_asset_injector.py | 健康资产注入 |
| 20260128/asset_audit_final.py | 资产审计 |
| 20260128/sovereignty_integrity_check.py | 主权完整性检查 |
| 20260128/run_trinity_oncology_case.py | Trinity 肿瘤案例 |
| 20260128/test_amani_v4_full_loop.py | V4 全流程测试 |
| 20260128/check_v4_baseline.py | V4 钢印与核心文件检查 |
| 20260128/verify_accuracy.py / verify_sovereignty_search.py | 验证脚本 |
| 20260128/match_patient.py / run_single_profile.py | 患者匹配与单例 |
| 20260128/trinity_dispatcher_final.py | Trinity 调度 |
| 20260128/amah_system_audit.py / amah_ui_demo.py / amah_viz.py 等 | 审计与展示 |

### 2.8 数据文件（JSON / CSV / JSONL）

| 相对路径 | 说明 |
|----------|------|
| 20260128/expert_map_data.json | 专家/PI 表 |
| 20260128/hospital_center_assets.json | 医院/中心表 |
| 20260128/merged_data.json | 临床试验主库 |
| 20260128/merged_data_cleaned.json | 清洗后试验 |
| 20260128/all_trials.json | 补充试验 |
| 20260128/global_elite_experts.json | 精英中心 |
| 20260128/physical_node_registry.json | AGID→物理节点（由 sync 脚本生成） |
| 20260128/patient_coverage_by_region.json | 区域患者覆盖（聚合、去标识） |
| 20260128/nebula_data.json / precision_kg.json | 知识/图数据 |
| 20260128/amani_finetuning_dataset.jsonl | 微调数据集 |
| 20260128/global_medical_assets.csv | 全球医疗资产表 |

### 2.9 文档（Markdown）

| 相对路径 | 说明 |
|----------|------|
| 20260128/CURSOR_AMANI_WORK_SUMMARY.md | Cursor 工作总览 |
| 20260128/SYSTEM_AUDIT_REPORT_AMANI.md | 系统审计报告 |
| 20260128/MEDICAL_REASONER_ORCHESTRATOR_EVALUATION.md | MedicalReasoner/Orchestrator 评估 |
| 20260128/FEASIBILITY_REVIEW_FOUR_PHASES.md | 四阶段可行性评审 |
| 20260128/TRINITY_ONCOLOGY_RUN_LOG.md | Trinity 肿瘤运行日志 |
| 20260128/WORK_LOG_TRINITY_V4_20260128.md | V4 工作日志 |
| 20260128/CLAUDE_CODE_AUDIT_MANIFEST.md | 本文件（Claude Code 审核调用清单） |

### 2.10 asset_library_l2 目录

| 相对路径 | 职责 |
|----------|------|
| 20260128/asset_library_l2/01_existing_assets.md | 已有资产类型与数量 |
| 20260128/asset_library_l2/02_ingestion_spec.md | 纳入规范（trial/pi/hospital/patient_coverage） |
| 20260128/asset_library_l2/03_cultural_main_complaint_equalizer.md | 主诉均等化说明 |
| 20260128/asset_library_l2/README.md | L2 资产库说明 |
| 20260128/asset_library_l2/asset_ingest.py | 资产纳入 CLI（trial/pi/hospital/patient_coverage） |
| 20260128/asset_library_l2/ingest_csv_assets.py | CSV 纳入 |
| 20260128/asset_library_l2/load_0131global_medical_assets.py | 加载 0131 全球资产 |
| 20260128/asset_library_l2/cultural_complaint_mapping.json | 主诉→规范英文映射 |
| 20260128/asset_library_l2/top100_hospitals_data.json | 前 100 医院源数据 |
| 20260128/asset_library_l2/sample_hospitals.json | 示例医院 |
| 20260128/asset_library_l2/new_assets_20260202.csv | 新资产 CSV |
| 20260128/asset_library_l2/working_log.jsonl | 纳入流水日志 |
| 20260128/asset_library_l2/working_log.md | 纳入流水（可读） |
| 20260128/asset_library_l2/0131global_medical_assets | 0131 资产数据 |
| 20260128/asset_library_l2/继续使用Python查找医疗资产的具体要求.txt | 资产查找要求说明 |

---

## 三、Claude Code 调用顺序建议（审核时加载顺序）

按「先配置与入口，再各层实现，再资产与数据，最后文档」顺序调用，便于理解依赖与数据流。

1. **配置与入口**  
   - `20260128/config.py`  
   - `20260128/amah_config.json`  
   - `20260128/app.py`  

2. **Trinity 主桥与 L1–L4**  
   - `20260128/amani_trinity_bridge.py`  
   - `20260128/amani_core_v4.py`  
   - `20260128/amani_nexus_layer_v3.py`  
   - `20260128/amani_interface_layer_v4.py`  
   - `20260128/amani_value_layer_v4.py`  
   - `20260128/amani_global_nexus_v4.py`  
   - `20260128/amah_centurion_injection.py`  
   - `20260128/amani_cultural_equalizer_l2.py`  
   - `20260128/medical_reasoner.py`  

3. **脑模型、计费、API**  
   - `20260128/amani_brain.py`（或 amani_brain_v4.py）  
   - `20260128/billing_engine.py`  
   - `20260128/trinity_api_connector.py`  

4. **资产与同步**  
   - `20260128/sync_l2_to_chromadb.py`  
   - `20260128/batch_build_db.py`  
   - `20260128/asset_library_l2/asset_ingest.py`  
   - `20260128/asset_library_l2/01_existing_assets.md`  
   - `20260128/asset_library_l2/02_ingestion_spec.md`  
   - `20260128/asset_library_l2/03_cultural_main_complaint_equalizer.md`  

5. **审计与总览文档**  
   - `20260128/SYSTEM_AUDIT_REPORT_AMANI.md`  
   - `20260128/CURSOR_AMANI_WORK_SUMMARY.md`  
   - `20260128/MEDICAL_REASONER_ORCHESTRATOR_EVALUATION.md`  

6. **其余文件**  
   - 按需按「二、按类型与层级」中的表格逐类加载（外部 API、诊断、数据文件等）。

---

## 四、如何用 Claude Code 审核本项目

- **工作区根：** 打开 `AMANI Project` 为根目录。  
- **主目录：** 所有代码与资产在 `20260128/` 下；L2 资产库在 `20260128/asset_library_l2/`。  
- **调用方式：**  
  - 将本文件 `20260128/CLAUDE_CODE_AUDIT_MANIFEST.md` 作为首条上下文提供给 Claude Code。  
  - 按「三、调用顺序建议」依次 @ 或打开对应文件进行审核。  
  - 需要全量文件列表时，以「二、按类型与层级」中的表格为准；路径均为相对项目根的相对路径。  
- **审核重点（可作提示词）：**  
  - L1 熵门与 D≤0.79、方差阈值是否与 amah_config 一致；  
  - Trinity 与 Centurion 双轨是否在 app 中统一为 TrinityBridge.run_safe；  
  - 凭证是否全部经 config 与环境变量、无硬编码；  
  - NexusRouter 是否依赖 physical_node_registry 与 sync_l2_to_chromadb；  
  - L2 主诉均等化是否在 L2.5 语义路径前调用；  
  - MedicalReasoner / Orchestrator / BatchProcessQueue 与配置是否一致；  
  - 资产纳入规范与 01_existing_assets、02_ingestion_spec 是否一致。

---

*End of Claude Code Audit Manifest*
