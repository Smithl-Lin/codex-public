# AMANI 无死角审计报告（Phase 1: 静态资产扫描与依赖审计）

- Date: 2026-02-12
- Auditor Role: Chief Technical Auditor
- Scope: `C:\2025-12-01 Mayo-working\2026-01-22 Business projects\AMANI Project`

## 1) 资产全景与核心模块识别

### 1.1 一级目录
- `20260128`：主代码、模型编排、数据资产、测试、审计文档
- `20260211`：治理规则与 worklog 归档
- `CODEX_WORKSPACE`：历史审计副本与工作文档
- `context.md`：上下文目录（作为目录存在）

### 1.2 代码资产分布（`20260128`）
- Python: 100 个
- Markdown: 27 个
- JSON: 19 个
- 其余为日志/二进制/数据库缓存

### 1.3 核心模块（按业务能力）
- AI 预测与决策核心：
  - `20260128/amani_core_v4.py`
  - `20260128/amani_brain.py`
  - `20260128/amani_brain_v4.py`
  - `20260128/medical_reasoner.py`
- 全球医疗资源调度与路由：
  - `20260128/amani_trinity_bridge.py`
  - `20260128/amani_nexus_layer_v3.py`
  - `20260128/amani_global_nexus_v4.py`
  - `20260128/amani_interface_layer_v4.py`
- 价值与计费闭环：
  - `20260128/amani_value_layer_v4.py`
  - `20260128/billing_engine.py`
- 资产注入与向量数据库：
  - `20260128/sync_l2_to_chromadb.py`
  - `20260128/batch_build_db.py`
  - `20260128/expert_bulk_loader.py`
  - `20260128/amah_centurion_injection.py`
- 外部 API 聚合：
  - `20260128/batch_fetch.py`
  - `20260128/nci_fetch.py`
  - `20260128/fda_device_fetch.py`
  - `20260128/frontier_special_aggregator.py`

## 2) 依赖审计（requirements vs 实际导入）

### 2.1 已声明关键依赖
- `streamlit`, `pandas`, `numpy`, `python-dotenv`, `chromadb`, `openai`, `anthropic`, `google-cloud-aiplatform`, `google-auth`, `aiolimiter`

### 2.2 发现的未声明但被代码实际使用依赖（高风险）
- `requests`（多处 API 拉取）
- `google-generativeai`（`genai`）
- `tqdm`
- `matplotlib`
- `pydeck`
- `fpdf`
- `Bio`（Biopython）
- `langchain_openai`

风险说明：部署环境若仅按 `requirements.txt` 安装，将出现运行时 ImportError，直接影响上线稳定性与医疗匹配任务可用性。

## 3) 冗余/重复逻辑与资产异常

### 3.1 重复脚本与命名异常
- `20260128/blitz_expansion_v2.py`
- `20260128/nano blitz_expansion_v2.py`

两者内容高度重复，仅存在少量文案差异（20k/200k描述偏差），属于高概率误保留副本，会导致执行入口混乱。

### 3.2 文件角色混淆
- `20260128/merged_data.json.py`

该文件实为脚本却带 `.json.py` 命名，且脚本内部逻辑/提示存在不一致（读 `merged_data.json` 却提示找不到 `all_trials.json`），属高风险误导点。

### 3.3 非标准命名资产
- `20260128/Mayo Internal Ref VERIFIED`

含特殊字符与空格，且内容为 Streamlit 片段，疑似临时摘录文件，跨平台与流水线处理风险较高。

## 4) 初步风险分级（Phase 1）

### 致命（Fatal）
1. 依赖清单与实际导入不一致（生产可直接崩溃）。

### 严重（High）
1. 重复脚本导致执行路径不确定（调度结果与扩容规模可能偏离预期）。
2. 脚本命名与行为混乱（`merged_data.json.py`），影响数据构建可靠性。

### 一般（Medium）
1. 非标准文件命名与临时资产混入主目录，影响维护与自动化流程。
2. 版本并存文件（v2/v2_5/v4）缺乏统一“唯一生产入口”标记，审计与变更成本高。

## 5) 优化方向（以“延迟下降 + 匹配成功率提升”为核心）

1. 依赖治理标准化
- 建立“运行时最小依赖集 + 开发依赖集”，冻结版本并校验可安装性。
- 预期收益：部署失败率明显下降，冷启动可控。

2. 执行入口收敛
- 统一每条业务链的唯一入口（采集、入库、匹配、审计），将重复/临时脚本迁出主路径。
- 预期收益：减少误执行导致的回滚与人工排障时间。

3. 数据通道一致性修复
- 统一 `merged_data`/`all_trials` 数据契约与脚本命名，避免静态资产与代码语义错配。
- 预期收益：提高训练/匹配输入质量稳定性，减少数据脏读。

4. 模块边界明确化
- 在 `Trinity Bridge / Nexus / Value / Interface` 之间补“输入输出契约文档 + 验证器”。
- 预期收益：降低跨模块耦合引发的连锁故障，改善迭代速度。

## 6) 预期性能提升（完成 Phase 1 修复后）
- 部署可用性：显著提升（核心路径 ImportError 风险收敛）
- 任务执行延迟：中度降低（减少误脚本执行和重复计算）
- 医疗匹配成功率：中度提升（数据构建链路一致性增强）

## 7) 下一步（进入 Phase 2 前置门槛）
- 先完成 `AUDIT_TASK_IDS_PHASE1.md` 中的 P0/P1 任务。
- 完成后进入 Phase 2：
  - Alpha Medical Asset Nexus Intelligence 鲁棒性与偏置审查
  - 全球调度算法多时区/多语言延迟与精度审查
  - HIPAA/GDPR 级安全与传输审查
