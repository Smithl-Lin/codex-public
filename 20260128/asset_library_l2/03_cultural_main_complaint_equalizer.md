# L2 主诉均等化 — 不同文化背景患者主诉分析与平权文本

**Stamp:** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN  
**Purpose:** 纳入不同文化背景的语言输入（主诉），生成平权、规范文本供下游模型分析；数据化、均等化，无 PII。  
**Layer:** L2（资产/编排层）；在 StaircaseMappingLLM / MedicalReasoner 之前调用。  
**Last Updated:** 2026-02-01  

---

## 1. 用途

- **输入：** 患者/客户主诉（chief complaint），任意支持语言/文化表述（如中文、英文、粤语、日语、韩语、德法西等）。  
- **输出：** 规范化的、文化中立的**平权文本**（canonical English clinical phrasing），供下游 L2.5/L3 模型分析，保证不同文化背景输入在语义层均等化。  
- **数据化：** 通过 `cultural_complaint_mapping.json` 维护「源表述 → 规范表述」映射；可扩展 locale、短语与类别。  

---

## 2. 文件位置（第几层）

| 文件 | 层级 | 说明 |
|------|------|------|
| **asset_library_l2/cultural_complaint_mapping.json** | L2 配置 | 多语言/文化主诉短语 → 规范英文临床表述映射表 |
| **amani_cultural_equalizer_l2.py** | L2 模块（20260128/） | 均等化逻辑：加载映射、检测 locale、输出 equalized_text |
| **amani_trinity_bridge.py** | L1 之后、L2.5 之前 | 在 run() 内调用 equalize_main_complaint(input_text)，将 text_for_l2 传入 semantic_path |

**调用顺序：** 用户输入 → L1 熵门 → **L2 主诉均等化**（equalize_main_complaint）→ L2.5 semantic_path（StaircaseMappingLLM/MedicalReasoner）→ L3 → L4。  

---

## 3. 配置说明（cultural_complaint_mapping.json）

- **phrase_mappings：** 每条含 `source_phrases`（多语言同义表述）、`canonical_complaint`（规范英文）、`category`（meta/symptom/condition/intent/treatment）。  
- **locale_detection_rules：** 可选，按字符集推断 locale（zh/ja/ko/ar/default）。  
- **output_language：** 规范输出语言，当前为 en。  
- **equalization_policy：** 仅用于下游分析；文化中立；禁止 PII。  

---

## 4. 使用方式

### 4.1 在管线中（已接入）

TrinityBridge.run() 已自动在 L2 前调用均等化；无需额外调用。  

### 4.2 单独调用

```python
from amani_cultural_equalizer_l2 import equalize_main_complaint, equalize_for_analysis

# 仅要平权文本
text = equalize_main_complaint("患者主诉：帕金森，寻求DBS评估。", locale_hint=None)

# 要完整结果（含 detected_locale、canonical_phrases）
out = equalize_for_analysis("患者主诉：帕金森，寻求DBS评估。")
# out["equalized_text"] 供下游模型
```

### 4.3 扩展映射

编辑 `asset_library_l2/cultural_complaint_mapping.json`，在 `phrase_mappings` 中追加 `source_phrases` 与 `canonical_complaint`，保存即可生效。  

---

## 5. 说明

- 本模块**不处理患者个人可识别信息（PII）**；仅对主诉文本做表述规范化与均等化。  
- 平权文本用于**模型输入均等化**，避免因语言/文化差异导致下游推理偏差；不改变临床含义。  

*End of 03_cultural_main_complaint_equalizer*
