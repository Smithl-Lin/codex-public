# AMANI 实证审计报告（Vision 全量收口）

- 日期: 2026-02-12
- 审计范围: `C:\2025-12-01 Mayo-working\2026-01-22 Business projects\AMANI Project`
- 约束声明: 本报告仅基于仓库内 `*.py/*.json/*.csv/*.md` 实际内容；未在源码检出的项统一标注为 `Not Found in Source`。

## 第一部分：架构实体审计（Entity Verification）

### 1) 核心组件定义位置

| 逻辑实体 | 源码证据 |
|---|---|
| Trinity Bridge（三位一体桥接） | `20260128/amani_trinity_bridge.py:449` (`class TrinityBridge`), `20260128/amani_trinity_bridge.py:573` (`run_safe`) |
| Nexus Router（纽带路由/调度） | `20260128/amani_nexus_layer_v3.py:26` (`class NexusRouter`), `20260128/amani_nexus_layer_v3.py:37` (`register_physical_mapping`), `20260128/amani_nexus_layer_v3.py:54` (`resolve_agid`) |
| AGID 生成逻辑 | `20260128/amani_core_v4.py:85` (`to_agid`), `20260128/amani_trinity_bridge.py:34` (`to_agid`), `20260128/amani_nexus_layer_v3.py:17` (`_to_agid`) |
| AGID 映射逻辑 | `20260128/amani_core_v4.py:92` (`map_legacy_id_to_agid`), `20260128/amani_nexus_layer_v3.py:37`, `20260128/amani_nexus_layer_v3.py:54` |

### 2) Streamlit 解耦检查（UI 是否硬编码业务）

结论: **部分耦合仍存在**。

- UI 已调用后端主入口 `TrinityBridge.run_safe`：`20260128/app.py:101`，`20260128/app_v4.py:79`。
- 但 UI 层仍包含业务判定逻辑（关键词分科、步骤兜底、计费联动条件）：
  - 关键词路由: `20260128/app.py:58`、`20260128/app.py:60`、`20260128/app_v4.py:53`、`20260128/app_v4.py:55`
  - 计费与影子账单展示: `20260128/app.py:133`、`20260128/app.py:138`、`20260128/app_v4.py:132`、`20260128/app_v4.py:137`
- 判定: UI 与后端**未完全解耦**（UI 仍嵌入部分业务决策）。

### 3) `AMANI_MASTER_ASSET_DB_vFinal.csv` 调用链与字段校验

- 在代码中检索该文件调用链: `Not Found in Source`。
- 唯一命中为愿景文档文本引用: `AMANI_Unified_Vision.md:21`。
- 因此对该 CSV 的字段级严格校验实现: `Not Found in Source`。

补充（其他 CSV 入口现状）：
- `20260128/asset_library_l2/ingest_csv_assets.py:50`、`20260128/asset_library_l2/load_0131global_medical_assets.py:34` 使用 `csv.DictReader`。
- 字段校验为轻量级（如仅校验 `ID` 非空），未见强 schema/类型校验（如必填全集、类型断言、范围校验）。

## 第二部分：合规与边界审计（Compliance & Boundary Audit）

### 1) Patient Intent 与 PHI/PII 脱敏

结论: **已实现正则脱敏 + 加盐哈希**，并接入多条外发路径。

- 脱敏规则与盐化哈希:
  - 正则: `20260128/privacy_guard.py:7`-`20260128/privacy_guard.py:10`
  - 加盐哈希: `20260128/privacy_guard.py:13`-`20260128/privacy_guard.py:16`
  - 脱敏入口: `20260128/privacy_guard.py:19`
- 外发路径接入:
  - MedGemma 调用前脱敏: `20260128/medical_reasoner.py:110`-`20260128/medical_reasoner.py:117`
  - Trinity 多模型上下文脱敏: `20260128/trinity_api_connector.py:45`-`20260128/trinity_api_connector.py:50`
  - 数据合成外发脱敏: `20260128/data_synthesizer.py:63`-`20260128/data_synthesizer.py:70`
  - Unified Synergy 查询脱敏: `20260128/amah_unified_synergy.py:26`-`20260128/amah_unified_synergy.py:33`

### 2) 区域策略硬编码检查（中美 C 端 / HIPAA vs PIPL）

结论: **已存在配置驱动 + 代码分支**。

- 配置项:
  - `20260128/amah_config.json:46`-`20260128/amah_config.json:48`
- 合规门实现:
  - 区域策略矩阵: `20260128/amani_nexus_layer_v3.py:136`-`20260128/amani_nexus_layer_v3.py:145`
  - 从配置覆盖加载: `20260128/amani_nexus_layer_v3.py:153`-`20260128/amani_nexus_layer_v3.py:169`
  - 同意记录/校验: `20260128/amani_nexus_layer_v3.py:183`-`20260128/amani_nexus_layer_v3.py:189`
  - 数据驻留与 PIPL 分支: `20260128/amani_nexus_layer_v3.py:200`-`20260128/amani_nexus_layer_v3.py:204`

### 3) 确定性门禁（Deterministic Gates）

结论: **存在 if-else 规则门引擎**；`match-case` 形式 `Not Found in Source`。

- L1 熵门 + D 门:
  - `20260128/amani_trinity_bridge.py:89`、`20260128/amani_trinity_bridge.py:92`
  - `20260128/amani_trinity_bridge.py:97`-`20260128/amani_trinity_bridge.py:101`
- 合规门 if-else:
  - `20260128/amani_nexus_layer_v3.py:196`-`20260128/amani_nexus_layer_v3.py:206`
  - `20260128/amani_nexus_layer_v3.py:224`-`20260128/amani_nexus_layer_v3.py:243`
- 多模型一票否决门:
  - `20260128/trinity_api_connector.py:100`-`20260128/trinity_api_connector.py:104`

## 第三部分：愿景鸿沟分析（Vision-to-Execution Gap）

### 1) 文档 vs 代码：24小时自动调度 与 Shadow-billing

- 愿景文档中的 shadow billing 叙述:
  - `AMANI_Unified_Vision.md:10`
- 文档中“24小时自动调度”字样:
  - `Not Found in Source`（在 `AMANI_Unified_Vision.md` 未检出该字样）
- 定时任务实现:
  - 标准 `Cron/Task Scheduler/APScheduler` 调度实现: `Not Found in Source`
  - 现有仅见 12 小时后台线程扫描（非 cron）: `20260128/amah_centurion_injection.py:253`、`20260128/amah_centurion_injection.py:378`
- Shadow-billing 实现:
  - 价值层计费矩阵: `20260128/amani_value_layer_v4.py:138`
  - 计费引擎: `20260128/billing_engine.py:37`
  - UI 联动展示: `20260128/app.py:133`-`20260128/app.py:138`
  - 结论: **Shadow-billing 有实现，但“成功费合同化模型”未见统一可执行合同层定义**（跨路径一致性不足）。

### 2) 模型调用闭环：Fallback 策略

结论: **不是单一 API；存在多模型与回退路径**。

- 多模型并行调用:
  - `20260128/trinity_api_connector.py:115`（gpt/gemini/claude）
- 模型分支:
  - `20260128/trinity_api_connector.py:66`-`20260128/trinity_api_connector.py:77`
- 共识与 veto:
  - `20260128/trinity_api_connector.py:94`-`20260128/trinity_api_connector.py:111`
- 回退证据:
  - MedGemma 失败回退 stub: `20260128/medical_reasoner.py:73`-`20260128/medical_reasoner.py:74`
  - 配置 fallback 开关: `20260128/amah_config.json:17`

## 第四部分：交付物（Deliverables）

### A) 证据清单（Vision 要求 vs 实现）

| 功能点 | 愿景要求 | 实际实现 | 结论 |
|---|---|---|---|
| Trinity Bridge | 单一桥接调度 | `TrinityBridge.run_safe` 已实现 | 已实现 |
| Nexus Router | AGID 到物理节点路由 | `NexusRouter` + register/resolve 已实现 | 已实现 |
| AGID 全局标识 | 生成与映射闭环 | 多模块 `to_agid` + 映射函数已实现 | 已实现 |
| CSV 主资产库 `AMANI_MASTER_ASSET_DB_vFinal.csv` | 愿景提及主数据源 | 仅文档提及，无代码调用链 | `Not Found in Source` |
| 严格 CSV 字段校验 | 强校验 | 现有为 `DictReader` + 轻校验 | 部分缺口 |
| PHI/PII 脱敏 | 出站保护 | 正则 + 加盐哈希 + 多路径接入 | 已实现 |
| 中美区域差异策略 | HIPAA/PIPL 分流 | 配置 + ComplianceGate 分支 | 已实现 |
| 医疗边界确定性 | 规则门限输出 | L1 gate + 合规 gate + veto | 已实现 |
| 24h 自动调度 | 连续自动调度 | 无 cron；仅 12h 线程扫描 | 部分缺口 |
| Shadow-billing | 成功费价值闭环 | 引擎/价值层/UI 已有 | 已实现（合同化不足） |
| 多模型 fallback | 异常回退闭环 | gpt/gemini/claude + stub fallback | 已实现 |

### B) 逻辑死角（文档清晰但代码存在 TODO/pass 占位）

| 位置 | 现象 | 风险级别 |
|---|---|---|
| `20260128/amani_global_nexus_v4.py:21` | `__init__` 空实现 `pass` | 中 |
| `20260128/amani_trinity_bridge.py:183` | `except Exception: pass`（L2.5 reasoner 失败静默回退） | 中 |
| `20260128/amani_trinity_bridge.py:475` | 配置加载异常静默 | 低 |
| `20260128/amani_trinity_bridge.py:509` | Centurion 配置读取异常静默 | 低 |
| `20260128/amah_centurion_injection.py:291`、`20260128/amah_centurion_injection.py:303`、`20260128/amah_centurion_injection.py:382` | 索引/变更写入或循环异常 `pass` | 中 |
| `20260128/amani_nexus_layer_v3.py:168` | 配置加载异常 `pass` | 低 |

### C) 合规性风险报告（原始数据外发到外部 API 的非受控接口）

以下接口未见 `privacy_guard.redact_text` 出站防护，判定为高风险：

1. `20260128/audit_agent.py:61`-`20260128/audit_agent.py:64`
- 将 `patient_info` 与 `trial_data` 拼接后直接发送至 OpenAI。

2. `20260128/debug_api.py:65`-`20260128/debug_api.py:68`
- 将病例摘要片段直接发往 Gemini 诊断调用，无脱敏。

3. `20260128/forensic_debug.py:56`-`20260128/forensic_debug.py:62`
- 将病例摘要片段直接发往 Gemini 取证调用，无脱敏。

对比说明（已受控）：
- `20260128/medical_reasoner.py:110`、`20260128/trinity_api_connector.py:45`、`20260128/data_synthesizer.py:63`、`20260128/amah_unified_synergy.py:26` 已接入脱敏。

## 结论（远景审查任务完成度）

- 远景审查四大部分（实体、边界、鸿沟、交付）本次已按源码证据完成。
- 仍存在的明确缺口已标注：
  - `AMANI_MASTER_ASSET_DB_vFinal.csv` 代码调用链: `Not Found in Source`
  - 标准 24h cron/task 调度: `Not Found in Source`
  - 若干关键路径 `pass` 静默吞错未完全治理。

## 修复执行状态（2026-02-12 同步）

- 高风险:
  - 已完成 `audit_agent.py` / `debug_api.py` / `forensic_debug.py` 出站脱敏接入。
- 中风险:
  - 已完成 `amani_trinity_bridge.py` / `amah_centurion_injection.py` 关键静默分支可观测化。
  - `amani_global_nexus_v4.py` 初始化占位已改为显式初始化状态字段。
- 低风险:
  - 已完成 `amani_nexus_layer_v3.py` / `app.py` / `app_v4.py` 的配置预加载异常告警化。
