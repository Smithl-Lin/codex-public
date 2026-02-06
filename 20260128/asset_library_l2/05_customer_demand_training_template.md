# L2 客户需求 / 训练数据模版 — 高端主诉合成数据

**Stamp:** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN  
**Purpose:** 定义用于模型训练的客户需求（主诉）合成数据的 Schema 与数据源，确保模版已纳入项目资产说明。  
**Layer:** L2 资产/训练数据；与主诉均等化、硬锚点识别配合使用。  
**Last Updated:** 2026-01-28  

---

## 1. 模版说明

- **用途：** 高端医疗领域的主诉/咨询语态合成数据，用于 A.M.A.N.I. 模型训练（意图识别、资产分类、L1 熵目标等）。  
- **数据源文件：** `20260128/amani_training_10k.json`（由 `generate_high_end_data.py` 生成）。  
- **规模：** 10,000 条；四类资产均匀分布（BCI / Gene_Therapy / Stem_Cell / Clinical_Trial 各 2,500 条）。  

---

## 2. Schema（严格执行）

每条记录包含以下字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| **request_id** | string | 是 | 格式 `AM-REQ-2026-XXXXX`（5 位数字，00000–09999） |
| **original_inquiry** | string | 是 | 含具体医学术语的高端需求描述；多语态（急迫、专业咨询、海外求药等） |
| **standard_mapping** | string | 是 | 对应的标准医学术语（该条所属类别的规范表述） |
| **asset_category** | string | 是 | 资产类别：`BCI` / `Gene_Therapy` / `Stem_Cell` / `Clinical_Trial` |
| **l1_entropy_target** | number | 是 | L1 熵目标值，区间 [0.5, 0.9]，保留 4 位小数 |

---

## 3. 领域与真实性

- **BCI（脑机接口）：** Neuralink, BrainGate, Speech Neuroprosthesis, Synchron Stentrode, Paradromics 等；术语含 invasive cortical electrode, speech prosthesis, BCI for ALS, locked-in syndrome 等。  
- **基因治疗：** ELEVIDYS, Zolgensma, Casgevy, Lyfgenia, AAV, CRISPR-Cas9；DMD, SMA, sickle cell 等。  
- **干细胞/再生医学：** iPSC, dopaminergic neuron, cardiomyocyte, organoid, Parkinson, heart failure 等。  
- **高端临床研究：** mRNA cancer vaccine, bispecific antibody, ADC, CAR-T, KRAS G12C, personalized neoantigen 等。  

---

## 4. 生成脚本与可复现

- **脚本：** `20260128/generate_high_end_data.py`  
- **可复现：** `RANDOM_SEED = 2026`；同一环境多次运行得到相同 10k 条。  
- **输出路径：** 默认 `20260128/amani_training_10k.json`（脚本运行时的当前目录）。  

---

## 5. 与项目其他模块的关系

- **主诉均等化：** `original_inquiry` 可经 `amani_cultural_equalizer_l2.equalize_main_complaint()` 转为平权文本。  
- **硬锚点识别：** `original_inquiry` 中原子技术词由 `amah_config.hard_anchor_boolean_interception.atomic_technical_terms` 识别。  
- **资产分类：** `asset_category` 与 L3 检索类别及 04 硬锚点文档中的类别一致。  
- **L1 熵目标：** `l1_entropy_target` 可用于训练或校准 L1 熵门相关逻辑（仅作参考，非运行时强制）。  

---

## 6. 文件位置汇总

| 项目 | 路径 |
|------|------|
| 本模版说明 | asset_library_l2/05_customer_demand_training_template.md |
| 数据文件 | 20260128/amani_training_10k.json |
| 生成脚本 | 20260128/generate_high_end_data.py |

*End of 05_customer_demand_training_template*
