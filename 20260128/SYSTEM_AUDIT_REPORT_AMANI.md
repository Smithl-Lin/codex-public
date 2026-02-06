# A.M.A.N.I. 项目系统审计报告

**审计日期:** 2026-02-02  
**范围:** 20260128 代码库及关联资产  
**Stamp:** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN  

---

## 一、核心逻辑总结：5 层架构及调度逻辑

### 1.1 架构概览

项目采用 **Trinity Neural Logic + Centurion L2/L2.5/L3** 双轨架构，实现从用户输入到物理节点匹配的闭环。

| 层级 | 名称 | 实现位置 | 职责 |
|------|------|----------|------|
| **L1** | Sentinel（哨兵） | amani_trinity_bridge.ECNNSentinel / amani_core_v4 | Shannon 熵门控；D ≤ 0.79 强制；方差 ≤ 0.005；未通过则拦截并返回 intercept AGID |
| **L2** | 资产层（Centurion） | amah_centurion_injection | 4 组件：Global_Patient_Resources、Advanced_Therapeutic_Assets、Principal_Investigator_Registry、Lifecycle_Pulse_Monitor；仅当 D ≤ 0.79 时通过 get_latest_snapshot 访问 |
| **L2.5** | 价值/编排层 | amani_value_layer_v4.AMAHValueOrchestrator / amani_trinity_bridge.StaircaseMappingLLM | Shadow Quote、多阶段旅程规划；资产分类 Gold Standard / Frontier / Recovery |
| **L3** | Nexus（全局枢纽） | amani_global_nexus_v4.GlobalNexus / amani_trinity_bridge.GNNAssetAnchor / amani_nexus_layer_v3.NexusRouter | 接收 L2+L2.5 快照，产出 dispatch 结果；AGID→物理节点/区域/endpoint 映射；区域合规门控 |
| **L4** | 接口层 | amani_interface_layer_v4.UIPresenter | Shadow Quote 多模态输出（TEXT/STRUCTURED/HTML/MARKDOWN）；FeedbackOptimizer 资产权重更新 |

**Trinity 桥接（单入口）：** `amani_trinity_bridge.TrinityBridge.run_safe(input_text)`  
- 流程：Input → L1 熵门 → L2/2.5 语义路径（StaircaseMappingLLM）→ L3 GNN 锚定（GNNAssetAnchor）→ L4 多模态 UI。  
- L1 失败时返回拦截结果（不抛异常），L2/L3/L4 不执行。

**Centurion 调度（资产快照）：** `amah_centurion_injection.AMAHCenturionInjector.get_latest_snapshot(d_precision)`  
- 仅当 D ≤ 0.79 返回 L2 四组件快照；经 L2.5 附加 Shadow Quote 与旅程计划后，再交给 L3 GlobalNexus.dispatch。

**配置与主权协议：**  
- `amani_core_v4`：GLOBAL_PRECISION_THRESHOLD=0.79、VARIANCE_INTERCEPT_LIMIT=0.005、to_agid、StrategicInterceptError。  
- `amah_config.json`：precision_lock_threshold、manual_audit_threshold、trinity_audit_gate、weight_hardening 等。

---

## 二、完成文件清单：关键文件及职责

### 2.1 核心层（L1 / 配置 / AGID）

| 文件 | 职责 |
|------|------|
| amani_core_v4.py | L1 规则与协议；精度阈值、方差上限、AGID 生成；AMANICoreOrchestrator 全局匹配；billing 与 D≤0.79 联动 |
| amani_trinity_bridge.py | Trinity 统一入口；ECNNSentinel、StaircaseMappingLLM、GNNAssetAnchor；TrinityBridge.run / run_safe；L4 UIPresenter 调用 |
| amah_config.json | 项目配置：precision_lock_threshold、manual_audit_threshold、trinity_audit_gate、weight_hardening、geographical_anchor |

### 2.2 资产与编排层（L2 / L2.5）

| 文件 | 职责 |
|------|------|
| amah_centurion_injection.py | L2 四组件（GPR、ATA、PI Registry、Pulse Monitor）；SecondLayerOrchestrator；AMAHCenturionInjector；L2→L2.5→L3 调度 |
| amani_value_layer_v4.py | AMAHValueOrchestrator：商业逻辑、全生命周期策略、billing matrix（D≤0.79） |
| amani_global_nexus_v4.py | Layer 3 GlobalNexus：接收 L2+L2.5 快照，产出 nexus 结果 |

### 2.3 接口与 Nexus（L3/L4）

| 文件 | 职责 |
|------|------|
| amani_interface_layer_v4.py | UIPresenter（Shadow Quote 多模态）；FeedbackOptimizer（资产权重） |
| amani_nexus_layer_v3.py | NexusRouter（AGID→物理节点/区域/endpoint）；ComplianceGate（区域隐私） |

### 2.4 计费与审计

| 文件 | 职责 |
|------|------|
| billing_engine.py | AMAHBillingEngine；D≤0.79 计费联动；AGID 报价单 |
| trinity_api_connector.py | AMAHWeightedEngine：Gemini/Claude/GPT 加权共识、一票否决、审计工作流 |
| conflict_governance_v2_5.py | 冲突治理与共识 |
| consensus_lock.py | 共识锁定逻辑 |

### 2.5 应用入口与前端

| 文件 | 职责 |
|------|------|
| app.py | Streamlit UI；get_strategic_routing；AGID 与 D 展示；billing 联动 |
| app_v4.py | V4 闭环：阈值来自 amani_core_v4 + amah_config.json |

### 2.6 数据与资产

| 文件 | 职责 |
|------|------|
| batch_build_db.py | merged_data.json → ChromaDB mayo_clinic_trials |
| amah_mega_loader.py / amah_nebula_injection.py / blitz_expansion*.py | 专家/资产注入 ChromaDB expert_map_global |
| asset_library_l2/asset_ingest.py | L2 资产纳入：trial/pi/hospital → 对应 JSON + working log |
| asset_library_l2/ingest_csv_assets.py | CSV（含 BCI Clinical Trial/BCI Company）纳入资产库 |
| data_purifier.py | 清洗与 AGID 输出 |
| amani_data_miner.py | PubMed 等数据采集 |

### 2.7 外部 API 与爬虫

| 文件 | 职责 |
|------|------|
| batch_fetch.py / fetch_details.py | ClinicalTrials.gov API v2 |
| nci_fetch.py | NCI clinical-trials API |
| jrct_aggregator.py / frontier_special_aggregator.py | WHO TrialSearch / 前哨试验聚合 |
| fda_device_fetch.py | FDA device API |
| monitor_status.py | 试验状态巡检 |

### 2.8 脑模型与校准

| 文件 | 职责 |
|------|------|
| amani_brain.py / amani_brain_v4.py | Trinity 主脑、E-CNN、AGID 输出、权重与决策 |
| amah_weight_orchestrator.py | 权重编排与熵计算 |
| calibration_engine.py | 应力数据集、波形拦截、审计摘要 |

### 2.9 测试与诊断

| 文件 | 职责 |
|------|------|
| run_trinity_oncology_case.py | TrinityBridge.run_safe 肿瘤案例；L1/L2.5/L3/L4 与熵指标 |
| test_amani_v4_full_loop.py | execute_global_match 全流程 |
| check_v4_baseline.py | V4 钢印与核心文件检查 |
| sovereignty_integrity_check.py / asset_audit_final.py | 主权与资产审计 |

---

## 三、工作细节记录：已实现功能点

（基于代码注释、模块导出与调用关系整理）

- **L1 硬锁：** ECNNSentinel Shannon 熵、D≤0.79、方差≤0.005；拦截 AGID；StrategicInterceptError。  
- **L2 四组件：** 从 merged_data.json、all_trials.json、expert_map_data.json 加载；治疗资产标签过滤；PI 与项目关联；12 小时脉冲扫描与 changelog。  
- **L2.5：** StaircaseMappingLLM 阶梯分类（Gold Standard/Frontier/Recovery）；AMAHValueOrchestrator 全生命周期策略与 billing matrix。  
- **L3：** GlobalNexus.dispatch 汇总 L2/L2.5；GNNAssetAnchor GAT 风格 intent→AGID；NexusRouter 物理映射；ComplianceGate 区域合规。  
- **L4：** UIPresenter Shadow Quote 四种模态；TrinityBridge 中 L4 输出包含 structured/html/markdown/text。  
- **统一入口：** TrinityBridge.run_safe；AMAHCenturionInjector.get_latest_snapshot(d_precision)；AMANICoreOrchestrator.execute_global_match。  
- **计费：** billing_engine 与 D≤0.79 联动；Shadow Quote 与 value layer 打通。  
- **资产库：** asset_library_l2 已有资产清单、纳入规范、CSV/JSON 纳入脚本与 working log。  
- **多模型审计：** trinity_api_connector 中 Gemini/Claude/GPT 加权共识与一票否决。  
- **配置闭环：** amah_config.json + amani_core_v4 单源阈值；app_v4 仅从 core 与 config 读阈值。

---

## 四、运行流程梳理：用户输入到物理节点匹配

1. **用户输入**  
   - Streamlit：app.py / app_v4.py 文本输入 → get_strategic_routing(query) → 学科、D、AGID、steps/experts。  
   - 程序化：TrinityBridge.run_safe(input_text) 或 AMANICoreOrchestrator.execute_global_match(profile)。

2. **L1 门控**  
   - ECNNSentinel.monitor(input_text)：Shannon 熵与 D 计算；未通过则抛 StrategicInterceptError 或（run_safe）返回 intercept 结果，不进入 L2。

3. **L2 资产**  
   - 若走 Centurion：get_latest_snapshot(0.79) → 四组件快照（GPR、ATA、PI、Pulse）。  
   - 若走 Trinity：StaircaseMappingLLM.semantic_path → 阶梯策略与 intent_summary。

4. **L2.5 价值**  
   - Centurion 路径：_enrich_snapshot_via_layer_2_5 → Shadow Quote + Multi-point Journey。  
   - Trinity 路径：L2 策略已含 category，L4 用 UIPresenter 渲染 Shadow Quote。

5. **L3 枢纽与物理映射**  
   - Centurion：_dispatch_to_layer_3(enriched) → GlobalNexus.dispatch → nexus 结果（含 layer_2_summary、shadow_quote、journey_plan）。  
   - Trinity：GNNAssetAnchor.forward(semantic_path) → top-k AGIDs + scores。  
   - 物理节点：NexusRouter.resolve_agid(agid) → physical_node_id、region、endpoint；ComplianceGate 按区域做合规校验。

6. **L4 输出**  
   - TrinityBridge 中 L4：UIPresenter 输出 Shadow Quote 的 structured/html/markdown/text。  
   - App：前端展示 AGID、D、学科、steps、experts、计费相关。

7. **数据流简图**  
   - 用户输入 → L1(熵/D) → [L2 资产快照 / L2 语义路径] → L2.5(Shadow Quote + 旅程) → L3(GlobalNexus / GNNAssetAnchor) → NexusRouter.resolve_agid → 物理节点/区域/endpoint → L4 多模态 / UI。

---

## 五、待解决问题清单

### 5.1 TODO / 未完成逻辑

- **Trinity 与 Centurion 双轨未完全统一：** run_safe 与 get_latest_snapshot 两条入口，L3 一侧为 GNNAssetAnchor（Trinity）、一侧为 GlobalNexus（Centurion）；物理节点来源依赖 NexusRouter 注册，未与 ChromaDB/expert_map 自动同步。  
- **NexusRouter 注册为空：** 默认无 AGID→物理节点注册，需显式 register_physical_mapping；与 L2/L3 产出的 AGID 未做批量绑定脚本。  
- **StaircaseMappingLLM 未接真实 LLM：** 阶梯分类为规则（Diagnosis/Treatment/Recovery/Follow-up + index），未调用 Gemini/Claude 等。  
- **GNNAssetAnchor 资产表为随机向量：** _init_fake_assets 为随机 embedding，未对接真实资产表或 ChromaDB。

### 5.2 逻辑断层与缺失模块

- **App 与 TrinityBridge 未直连：** app/app_v4 使用 get_strategic_routing 规则路由，未调用 TrinityBridge.run_safe，因此 UI 未经过 L1 熵门与 L2.5/L3 Trinity 管线。  
- **execute_global_match 与 Trinity 脱节：** AMANICoreOrchestrator.execute_global_match 独立逻辑，未经过 ECNNSentinel 与 StaircaseMappingLLM。  
- **L2 组件与 ChromaDB 不同步：** L2 从 JSON 文件读取；批量注入脚本写的是 ChromaDB；两处需定期同步或统一数据源。  
- **未完成的 API 对接：** trinity_api_connector 使用 Vertex Gemini + Claude + OpenAI，key_path 硬编码为 `/home/smithlin/...`，非本机需改路径或环境变量；Gemini 模型名为 "gemini-3-pro-preview" 需与当前 Vertex 可用模型一致。

### 5.3 潜在安全与合规问题

- **API Key 硬编码：** forensic_debug.py、debug_api.py、data_synthesizer.py、check_models.py 中 `API_KEY = "AIzaSyCffk6PhYUxJ7htnvzquvslsTU10_FgA-8"` 明文，存在泄露风险；应改为环境变量或密钥管理服务。  
- **服务账号路径：** trinity_api_connector 中 key_path 写死，建议改为环境变量（如 GOOGLE_APPLICATION_CREDENTIALS）。  
- **合规与审计：** ComplianceGate 仅有框架，consent_store 与区域规则需按实际部署补充；医疗数据需满足 HIPAA/GDPR 等，当前未显式标注。

### 5.4 其他

- **variance 0.005 过严：** 长文本熵方差易超限，导致 L1 拦截率高；可考虑可配置或分场景阈值。  
- **中文/英文混用：** 部分脚本与注释仍为中文，与“专业英文”规范不完全一致，可逐步统一。

---

## 六、MedGemma 适配差额

（对照 Google MedGemma / Health AI 赛道常见要求）

### 6.1 MedGemma 赛道常见要求简述

- **模型：** 基于 Gemma 的医学文本/图像理解（如 MedGemma 1/1.5 4B 多模态、27B 文本等）。  
- **能力：** 医学文本理解、临床推理、分诊、决策支持、摘要；影像解释、解剖定位等。  
- **集成方式：** 本地（Hugging Face）、Vertex AI Model Garden、微调、批处理等。  
- **验证：** 需针对具体场景验证，非默认临床级。

### 6.2 当前代码与 MedGemma 的差距

| 维度 | 当前状态 | 差额 |
|------|----------|------|
| **医学专用基座** | 使用通用 Gemini/Claude/GPT（trinity_api_connector、data_synthesizer 等） | 未集成 MedGemma 或其它医学专用基座；无 MedGemma 调用或微调流水线 |
| **医学影像** | 无影像输入或影像专用模型 | 缺少影像管线与 MedGemma 多模态（影像）集成 |
| **临床推理链** | 规则 + 多模型加权共识 | 未使用 MedGemma 做诊断匹配、分诊或摘要等结构化临床推理 |
| **Vertex / Model Garden** | 使用 Vertex GenerativeModel，但模型名为 gemini-3-pro-preview | 未配置 Vertex 上的 MedGemma（如 Model Garden 部署）；未区分“通用 Gemini”与“MedGemma” |
| **微调与批处理** | 有 amani_finetuning_dataset.jsonl，无 MedGemma 微调脚本 | 缺少基于 MedGemma 的微调/适配流程与数据格式说明 |
| **L1/L2 语义** | L1 为熵/D 门控；L2.5 为规则阶梯 | 未将 MedGemma 用于意图理解、试验匹配或报告生成，未形成“MedGemma-in-the-loop”的闭环 |

### 6.3 建议的关键集成步骤

1. **模型接入：** 在 Vertex AI 或本地部署 MedGemma，提供统一推理接口（如 MedGemmaClient）；替换或并联 trinity_api_connector 中部分 Gemini 调用为 MedGemma（例如临床审计、摘要、匹配理由生成）。  
2. **意图与匹配：** 用 MedGemma 解析用户输入生成结构化意图/诊断/试验条件，再交给 StaircaseMappingLLM 或 GNN 锚定，形成“MedGemma 语义 + 现有 L2/L3”的管线。  
3. **影像管线（若赛道要求）：** 增加影像上传与预处理，调用 MedGemma 多模态做影像解读，结果并入现有 AGID/物理节点匹配流程。  
4. **微调与验证：** 使用 amani_finetuning_dataset 或自有医学数据，在 MedGemma 上做领域微调；对关键场景做准确率与安全性的验证并记录。  
5. **配置与安全：** 将 MedGemma 端点、模型 ID、配额等放入 amah_config 或环境变量，避免硬编码；API/密钥管理符合安全规范。

---

## 七、已实施修改（四阶段方案）

以下修改已按本报告「五、待解决问题」与「六、MedGemma 适配差额」落地，便于版本对照。

| 阶段 | 内容 | 涉及文件/产出 |
|------|------|----------------|
| **一、环境硬化与安全治理** | API/Key 与密钥路径不再硬编码；统一从环境变量读取 | config.py、.env.example、.gitignore；forensic_debug.py、debug_api.py、data_synthesizer.py、check_models.py 使用 get_gemini_api_key()；trinity_api_connector.py、gemini_diag.py 使用 get_google_credentials_path() / GOOGLE_APPLICATION_CREDENTIALS |
| **二、逻辑中枢归拢** | App 统一走 TrinityBridge.run_safe；L2 可选 Centurion 富化 | app.py：TrinityBridge.run_safe + _bridge_result_to_ui；amani_trinity_bridge.py：run() 内可选 centurion_snapshot；L4 影像上传 UI 桩 |
| **三、资产与物理路径硬化** | NexusRouter 启动时从注册表加载；GNNAssetAnchor 可接 ChromaDB | amani_nexus_layer_v3.py：NexusRouter.auto_register(registry_path)；sync_l2_to_chromadb.py → physical_node_registry.json；amani_trinity_bridge.py：GNNAssetAnchor(chromadb_path/collection_name) 支持 ChromaDB 语义查询 |
| **四、MedGemma 适配与模型重构** | MedicalReasoner 可配置 Endpoint；L4 影像批处理桩；配置段 | amah_config.json：medgemma 段；medical_reasoner.py：MedicalReasoner、Orchestrator、BatchProcessQueue；StaircaseMappingLLM 优先调用 MedicalReasoner；amani_interface_layer_v4.enqueue_image_for_batch 桩 |

**使用说明：** 复制 `.env.example` 为 `.env` 并填写凭证；部署/启动前可执行 `sync_l2_to_chromadb.py` 生成并注册物理节点表。

---

*报告结束。建议将本报告纳入版本管理与后续迭代对照。*
