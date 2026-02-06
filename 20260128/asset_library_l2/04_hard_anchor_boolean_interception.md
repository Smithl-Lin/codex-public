# L2/L3 硬锚点布尔拦截与百级检索池二次重排

**Stamp:** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN  
**Purpose:** 定义系统如何识别病历中的「原子级」技术词，以及百级检索池（N=100）二次重排机制，作为防止「降级匹配」的防火墙。  
**Layer:** 原子词识别在 L2 均等化后、L3 检索前；二次重排在 L3 检索内部。  
**Last Updated:** 2026-01-28  

---

## 1. 硬锚点布尔拦截逻辑 (Hard Anchor Boolean Interception)

### 1.1 定义

- **原子级技术词 (Atomic Technical Terms)：** 病历/主诉中出现的、不可被泛化替代的医学术语或技术标识，例如：
  - **神经/再生：** iPS, BCI, DBS, 脑机接口, 干细胞, Neural Interface, Neuralink, Dopaminergic, Subthalamic
  - **肿瘤/精准：** KRAS G12C, G12C, CAR-T, ADC, mRNA Vaccine
  - **其他：** 由 `amah_config.json` 的 `hard_anchor_boolean_interception.atomic_technical_terms` 维护，可扩展。

- **识别方式：** 对 L2 均等化后的文本（及原始主诉）做**大小写不敏感、子串匹配**；命中即记为该病例的「硬锚点集合」。不依赖 NER 模型，保证可解释与可审计。

- **布尔拦截含义：**  
  - **不**在 L1 做拦截（L1 仍为熵门 + D≤0.79）。  
  - 在 **L3 检索阶段** 使用：先在一大池子（百级）中召回，再按「是否覆盖硬锚点」做二次重排；若病例带硬锚点而最终 top-k 中无一覆盖，则视为潜在「降级匹配」，可打标或提升硬锚点匹配项的权重，从而形成防火墙。

### 1.2 与现有逻辑的关系

- **ontology_engine.py：** 已有 `MEDICAL_ONTOLOGY` 与 `enhance_query_with_ontology()`，产出 `hard_anchors` 与增强查询。  
- **本规范：** 将原子技术词统一纳入配置，并在 **L3 检索池与重排** 中显式使用硬锚点，而不仅用于查询增强。  
- **data_purifier / audit_agent：** 已有 BCI/iPS 等核心词过滤或审计表述；本规范与之对齐，并明确「识别 → 百级池 → 二次重排」的闭环。

---

## 2. 百级检索池（N=100）与二次重排机制

### 2.1 检索池规模

- **N=100：** 第一阶段从向量库（ChromaDB expert_map_global）按语义召回 **最多 100 条** 候选（由 `hard_anchor_boolean_interception.retrieval_pool_size_n` 配置，默认 100）。  
- **目的：** 避免「只取 top-k（如 5）导致高相关但带硬锚点匹配的资产被截断」，为二次重排提供足够候选。

### 2.2 二次重排规则（防降级匹配）

1. **输入：** 病例硬锚点集合 `H`（来自 1.1）、第一阶段的 N 条候选（id、score、documents/metadatas）。  
2. **覆盖判定：** 对每条候选，判断其 `documents` 或 `metadatas` 文本中是否包含 `H` 中**任意一个**原子技术词（大小写不敏感）。  
3. **重排策略：**  
   - **硬锚点优先：** 将「覆盖至少一个硬锚点」的候选排在前面，同一组内按原语义 score 降序。  
   - **无硬锚点时的回退：** 若病例未识别出硬锚点，或池中无覆盖硬锚点的候选，则按原语义 score 取 top-k，不改变顺序。  
4. **输出：** 从重排后的列表中取 **top-k**（如 5）作为最终 AGID 列表，保证在病例含 BCI/iPS/KRAS G12C 等时，优先返回同样包含这些技术词的专家/试验，从而防止降级匹配。

### 2.3 配置项（amah_config.json）

```json
"hard_anchor_boolean_interception": {
  "atomic_technical_terms": [
    "iPS", "BCI", "DBS", "KRAS G12C", "G12C", "CAR-T", "ADC", "干细胞", "脑机接口",
    "Neural Interface", "Neuralink", "Dopaminergic", "Subthalamic", "mRNA Vaccine"
  ],
  "retrieval_pool_size_n": 100,
  "re_rank_policy": "hard_anchor_first",
  "downgrade_firewall": true
}
```

- **atomic_technical_terms：** 原子级技术词列表，用于识别与覆盖判定。  
- **retrieval_pool_size_n：** 第一阶段召回数量，默认 100。  
- **re_rank_policy：** 固定为 `hard_anchor_first`（硬锚点优先）。  
- **downgrade_firewall：** 为 true 时启用上述二次重排；为 false 时仅做单阶段 top-k 召回（与原行为一致）。

---

## 3. 数据流小结

1. **用户输入** → L1 熵门 → L2 主诉均等化 → L2.5 语义路径（intent_summary）。  
2. **原子词识别：** 对均等化后文本（或原始主诉）做原子技术词匹配 → 得到硬锚点集合 `H`。  
3. **L3 第一阶段：** 用 intent_summary 在 ChromaDB 中召回 **N=100** 条候选。  
4. **L3 第二阶段：** 按硬锚点覆盖情况重排，取 **top-k** 输出给 L4。  
5. **防降级：** 病例带 BCI/iPS/KRAS G12C 等时，优先展示同样包含这些词的资源，避免「降级匹配」到泛化资产。

---

## 4. 文件与代码位置

| 项目 | 位置 |
|------|------|
| 本规范 | asset_library_l2/04_hard_anchor_boolean_interception.md |
| 配置 | amah_config.json → hard_anchor_boolean_interception |
| 原子词识别 | amani_trinity_bridge 内从 config 读取词表并做子串匹配；或调用 ontology_engine |
| 百级池 + 二次重排 | amani_trinity_bridge.GNNAssetAnchor.map_to_agids(retrieval_pool_n, hard_anchors, top_k) |

*End of 04_hard_anchor_boolean_interception*
