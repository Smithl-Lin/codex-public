# 用户诉求匹配逻辑 — 审核文档

**Stamp:** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN  
**Purpose:** 汇总当前系统对用户诉求（病历/主诉）的匹配逻辑，供审核与对照。  
**Last Updated:** 2026-01-28  

---

## 一、主入口与数据流概览

| 步骤 | 位置 | 输入 | 输出 |
|------|------|------|------|
| **入口** | app.py | 用户文本（patient_input） | 点击「启动 5.0x 本体论深度对位」→ TrinityBridge.run_safe(patient_input, top_k_agids=5) |
| **L1** | amani_trinity_bridge.ECNNSentinel | 原始 input_text | 通过 → l1_ctx（d_effective, variance）；不通过 → 抛 StrategicInterceptError，run_safe 返回 intercepted=True |
| **L2 均等化** | amani_cultural_equalizer_l2.equalize_main_complaint | input_text | text_for_l2（平权/规范文本，可选） |
| **L2.5 语义路径** | StaircaseMappingLLM.semantic_path | text_for_l2, l1_ctx | l2_path：strategy, intent_summary, asset_categories 等 |
| **硬锚点识别** | _extract_hard_anchors | input_text 或 text_for_l2 | hard_anchors（原子技术词列表） |
| **L3 检索与重排** | GNNAssetAnchor.forward → map_to_agids | l2_path（含 intent_summary, hard_anchors, retrieval_pool_size_n） | l3_out：agids, scores, intent_summary, hard_anchors_used |
| **L4 展示** | _bridge_result_to_UI | result | dept, D, agid, steps, experts_df |

**主链路代码位置：**  
- 入口：`app.py` 第 104–107 行（TrinityBridge.run_safe）  
- 管线：`amani_trinity_bridge.py` 中 TrinityBridge.run() 第 438–466 行  

---

## 二、L1：诉求是否被接纳（熵门与 D 阈值）

- **文件：** `amani_trinity_bridge.py`，ECNNSentinel（约 70–109 行）。
- **逻辑：**
  1. 对**原始用户输入**做按字符滑动窗口的 Shannon 熵计算，得到 `mean_entropy` 与 `variance`。
  2. `d_effective = min(1.0, 1.2 - mean_entropy * 0.3)`。
  3. **通过条件（与顺序）：**  
     - 先判 **variance ≤ variance_limit**（默认从 amah_config 的 `trinity_audit_gate.variance_limit_numeric` 读取，典型 0.05）；  
     - 再判 **d_effective ≤ d_threshold**（0.79）。
  4. 任一不满足即**不通过**，返回 intercept_agid，run_safe 捕获后返回 `intercepted: True`，**不进入 L2/L3 匹配**。
- **审核要点：**  
  - 匹配逻辑仅对「通过 L1」的诉求生效；未通过时无专家/试验匹配结果。  
  - 方差上限可配置，避免多语言/长文本被过度拦截。  

---

## 三、L2：主诉均等化（可选）

- **文件：** `amani_cultural_equalizer_l2.py`，`equalize_main_complaint()`；调用处在 TrinityBridge.run() 第 450–454 行。
- **逻辑：** 将原始主诉（多语言/文化表述）映射为规范、平权文本 `text_for_l2`，供下游 L2.5 使用；若未配置或异常则仍用原始 input_text。
- **审核要点：** 匹配使用的语义来自 **text_for_l2**（或原始输入），而非仅原始输入；均等化影响 intent 与策略，进而影响 L3 检索。  

---

## 四、L2.5：意图与策略（intent_summary 的来源）

- **文件：** `amani_trinity_bridge.py` 中 StaircaseMappingLLM.semantic_path（约 158–189 行）；内部调用 `medical_reasoner.MedicalReasoner.reason()` 与 `Orchestrator.run()`。
- **逻辑：**
  1. 优先调用 **MedicalReasoner.reason(text_for_l2, l1_ctx)**：  
     - 若配置了 MEDGEMMA_ENDPOINT，则请求 MedGemma，返回含 strategy、intent_summary、resource_matching_suggestion 的 JSON。  
     - 未配置则走 **stub**：规则生成 strategy（Diagnosis/Treatment/Recovery/Follow-up + Gold Standard/Frontier/Recovery），**intent_summary = input_text[:200]**。
  2. 再经 **Orchestrator.run()** 做主权审计（reasoning_cost、compliance_score、路径截断/脱敏），输出写入 payload。
  3. semantic_path 返回的 **l2_path** 包含：  
     - **intent_summary**：来自 MedicalReasoner（或 stub 的 input_text[:200]），**作为 L3 检索的查询文本**。  
     - strategy、asset_categories、resource_matching_suggestion、orchestrator_audit 等。
- **审核要点：**  
  - 当前 stub 下 **intent_summary 仅为输入前 200 字符**，未做深度意图抽取。  
  - 真实 MedGemma 接入后，intent_summary 将影响 L3 语义检索质量。  

---

## 五、硬锚点识别（原子技术词）

- **文件：** `amani_trinity_bridge.py`，`_extract_hard_anchors(text, base_dir)`（约 210–227 行）；TrinityBridge.run() 第 456–463 行注入 l2_path。
- **逻辑：** 对 **input_text 或 text_for_l2** 做**大小写不敏感子串匹配**，词表来自 `amah_config.json` 的 `hard_anchor_boolean_interception.atomic_technical_terms`（如 iPS, BCI, DBS, KRAS G12C, 干细胞, 脑机接口 等）。  
- **用途：** 供 L3 二次重排使用，防止降级匹配（见下）。  

---

## 六、L3：从意图到 AGID（检索与重排）

- **文件：** `amani_trinity_bridge.py`，GNNAssetAnchor.map_to_agids（约 287–368 行）、forward（约 370–393 行）。
- **输入：** semantic_path（l2_path）中的 **intent_summary**、**hard_anchors**、**retrieval_pool_size_n**（默认 100）、**downgrade_firewall**（默认 True）。
- **逻辑：**
  1. **第一阶段（检索池）：**  
     - 使用 ChromaDB 集合 **expert_map_global**（路径 amah_vector_db，由 expert_bulk_loader 写入）。  
     - `query_texts=[intent_summary[:2000]]`，`n_results=min(retrieval_pool_size_n, count)`，默认 **N=100**。  
     - 得到候选列表（id, score, documents, metadatas）。
  2. **第二阶段（二次重排，防降级）：**  
     - 若 **hard_anchors 非空且 downgrade_firewall=True**：  
       - 对每条候选的 documents/metadatas 文本做**是否包含任意硬锚点**的判定（大小写不敏感）。  
       - 将候选分为「覆盖至少一个硬锚点」与「未覆盖」两类；**覆盖者优先**，同类内按原 score 降序。  
     - 否则仅按原 score 降序。
  3. **输出：** 从重排后列表中取 **top_k**（默认 5）个 (agid, score)，作为 l3_nexus.agids / l3_nexus.scores。
- **审核要点：**  
  - 匹配对象是 **expert_map_global** 中的专家/PI 文档（name, affiliation, specialty, expertise_tags, value_add_services 等拼接成的文本）。  
  - 未使用 medical_db / mayo_clinic_trials 做试验级匹配；试验匹配若需可在此后或并行扩展。  
  - 硬锚点重排确保「含 BCI/iPS/KRAS G12C 等诉求」优先对应同样含这些技术词的资产。  

---

## 七、L4：结果到 UI 的映射

- **文件：** `app.py`，`_bridge_result_to_UI(result)`（约 42–64 行）。
- **逻辑：**
  - **dept（科室）：** 对 `result._input_text` 做**关键词启发式**：  
    - 含 "parkinson"/"dbs"/"bci"/"脑"/"帕金森" → Neurology；  
    - 含 "癌"/"瘤"/"肿"/"cancer"/"metastasis" → Oncology；  
    - 否则取 strategy[0].category 或 "Complex-Cases"。  
  - **D：** l1_sentinel.d_effective（默认 0.79）。  
  - **agid / steps：** 来自 l3_nexus.agids[0] 与 l2_2_5_semantic_path.strategy。  
  - **experts_df：** 由 l3_nexus.agids[:10] 与 scores[:10] 组成表格；**无物理节点名称/机构名**，仅 AGID 与分数。
- **审核要点：**  
  - 科室为**规则关键词**，与 L3 检索结果无直接绑定。  
  - 若需展示「专家姓名/机构」，需用 AGID 反查 NexusRouter / physical_node_registry 或 expert_map 元数据。  

---

## 八、其他与诉求匹配相关的路径（非主链路）

| 路径 | 文件 | 说明 |
|------|------|------|
| **get_strategic_routing** | app.py 67–87 行 | 仅当未走 TrinityBridge 时的备用路由；按关键词返回固定科室、D、AGID、steps、experts；**不经过 L1/L2/L3 管线**。当前主按钮已走 run_safe，此函数为遗留或备用。 |
| **amah_viz** | amah_viz.py | 独立 Streamlit 页：用户输入 → ChromaDB expert_map_global.query(query_texts=[user_input], n_results=10)，再经 AMAHPatentEngine 阶梯逻辑与分值；**不经过 TrinityBridge**。 |
| **amah_unified_synergy** | amah_unified_synergy.py | 先查 neurology_assets，再查 expert_map_global，再三路博弈审计与计费；**不经过 L1 熵门与 TrinityBridge**。 |
| **amah_full_pipeline** | amah_full_pipeline.py | 仅查 neurology_assets，再交三路引擎审计；**无专家级匹配**。 |
| **match_patient / test_basket_match / verify_accuracy** | 各脚本 | 直接对 ChromaDB 做 query_texts，用于测试或验证；**不经过 TrinityBridge**。 |

主入口审核以 **app.py → TrinityBridge.run_safe → run()** 为准；上述其他路径不参与「主链路用户诉求匹配」审核。  

---

## 九、配置与可调参数（与匹配相关）

| 配置项 | 文件 | 作用 |
|--------|------|------|
| trinity_audit_gate.variance_limit_numeric | amah_config.json | L1 方差上限，超过则拦截；默认 0.05。 |
| alignment_logic.precision_lock_threshold | amah_config.json | L1 D 阈值，默认 0.79。 |
| hard_anchor_boolean_interception.atomic_technical_terms | amah_config.json | 原子技术词表，用于硬锚点识别与 L3 重排。 |
| hard_anchor_boolean_interception.retrieval_pool_size_n | amah_config.json | L3 第一阶段检索池大小，默认 100。 |
| hard_anchor_boolean_interception.downgrade_firewall | amah_config.json | 是否启用硬锚点二次重排，默认 true。 |
| ChromaDB 路径 / 集合 | TrinityBridge.__init__, GNNAssetAnchor | amah_vector_db，expert_map_global；决定匹配数据源。 |
| top_k_agids | app.py 调用 run_safe(..., top_k_agids=5) | L3 最终返回的 AGID 数量。 |

---

## 十、审核结论摘要

1. **主链路：** 用户诉求匹配由 **TrinityBridge.run_safe** 驱动，经 L1（熵门+D）→ L2 均等化（可选）→ L2.5 语义路径（intent_summary）→ 硬锚点识别 → L3 百级池检索 + 硬锚点重排 → top_k AGID，再经 _bridge_result_to_UI 转为界面展示。  
2. **匹配对象：** 当前仅对 **expert_map_global**（专家/PI）做语义检索与重排；试验库（medical_db / mayo_clinic_trials）未在本管线中参与匹配。  
3. **意图表示：** stub 下 intent_summary 为输入前 200 字符；接入 MedGemma 后可改为模型生成的简洁意图，影响 L3 检索质量。  
4. **防降级：** 通过硬锚点词表与 N=100 二次重排实现，诉求含原子技术词时优先返回同样含该词条的资产。  
5. **科室与展示：** 科室由输入侧关键词规则决定；表格中仅 AGID+Score，若需专家/机构名需额外解析或查表。  

*End of User Request Matching Logic Audit*
