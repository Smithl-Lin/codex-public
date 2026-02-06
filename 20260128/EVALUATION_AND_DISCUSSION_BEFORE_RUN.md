# 修改建议评价与讨论（运行前）

**角色：** AI 专家  
**日期：** 2026-01-28  
**目的：** 综合当前修改建议给出评价，讨论后再执行初始化与启动。  
**Stamp：** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN  

---

## 一、对审核结论的总体评价

### 1.1 结论：**同意审核结论，建议按步骤执行前先做一次状态检查**

| 审核结论 | 评价 |
|----------|------|
| 架构 8.5/10、五层完整、D≤0.79 一致、无硬编码凭证 | ✅ **准确**，与现有代码和 CURSOR_AMANI_WORK_SUMMARY 一致 |
| 3 个关键阻塞项（ChromaDB、physical_node_registry、.env） | ✅ **合理**，但需澄清两点（见下） |
| 建议改进（Gemini 模型名、E2E 测试、requirements.txt） | ✅ **有价值**，新建文件已到位 |
| 快速启动 4 步（verify → pip install → 初始化 3 脚本 → streamlit） | ✅ **顺序正确**，建议先执行 verify 再决定是否全量初始化 |

---

## 二、关键澄清与补充（执行前必读）

### 2.1 ChromaDB：存在两个库路径，职责不同

| 脚本 | ChromaDB 路径 | 集合 | 用途 |
|------|----------------|------|------|
| **expert_bulk_loader.py** | `./amah_vector_db` | expert_map_global | **Trinity L3 GNNAssetAnchor 使用**，语义检索 AGID → 物理节点 |
| **batch_build_db.py** | `./medical_db` | mayo_clinic_trials | 临床试验语义库；Centurion/其他组件可能使用 |

- **verify_prerequisites.py** 只检查 `amah_vector_db/` 和 `expert_map_global`，与 Trinity 主路径一致。
- **若要完整功能**（试验检索 + 专家检索）：需同时运行 **batch_build_db.py** 与 **expert_bulk_loader.py**，会得到两个目录：`medical_db/` 与 `amah_vector_db/`。
- **若仅验证 Trinity 主流程**：只运行 **expert_bulk_loader.py** 即可（L3 依赖 amah_vector_db）。

**建议：** 执行时两个脚本都跑一遍，避免后续其他模块依赖 mayo_clinic_trials 时报错。

---

### 2.2 physical_node_registry.json：可能已存在

- 当前仓库中 **已存在** `20260128/physical_node_registry.json`（此前运行过 sync_l2_to_chromadb.py 时生成）。
- **执行前** 先运行 `python verify_prerequisites.py`：若已报「物理节点注册表: N 个映射」且 N>0，则**无需再跑** sync_l2_to_chromadb.py，除非你修改了 expert_map 或 hospital_center 并希望重新生成注册表。

---

### 2.3 环境变量 .env

- `.env` 通常被 .gitignore，列表中不可见不等于不存在。
- **必须** 至少配置一个 LLM API key（GEMINI_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY），否则多模型审计与部分 L2.5 能力不可用。
- 若使用 Vertex Gemini，还需配置 **GOOGLE_APPLICATION_CREDENTIALS**（服务账号 JSON 路径）。

---

### 2.4 Gemini 模型名称（建议改进项）

- **现状：** `trinity_api_connector.py` 中使用 `GenerativeModel("gemini-3-pro-preview")`。
- **风险：** Vertex 上若已更名或下线该模型，调用会失败。
- **建议：** 将模型名迁至 `amah_config.json` 或环境变量，便于按环境切换；或改为当前 Vertex 可用名称（如 gemini-1.5-pro）。

---

## 三、建议执行顺序（讨论后再运行）

### 第一步：状态检查（不改变数据）

```bash
cd "C:\2025-12-01 Mayo-working\2026-01-22 Business projects\AMANI Project\20260128"
python verify_prerequisites.py
```

- 若 **全部通过**：可直接执行第四步启动 Streamlit（若仅做 UI 与 L1 演示，可不跑初始化）。
- 若 **有失败项**：按输出提示逐项修复（见下）。

### 第二步：依赖安装（如需）

```bash
pip install -r requirements.txt
```

- 若 verify 中「Python 依赖检查」已通过，可跳过。

### 第三步：数据与注册表初始化（按需）

- **ChromaDB 未初始化 / 缺少 expert_map_global：**
  - `python expert_bulk_loader.py`  # 必须，供 Trinity L3 使用
  - `python batch_build_db.py`     # 建议，供试验检索等完整功能
- **physical_node_registry.json 不存在或为空：**
  - `python sync_l2_to_chromadb.py`
- **.env 未配置或 API key 缺失：**
  - 复制 `.env.example` 为 `.env`，至少填入一个 LLM API key（及 GOOGLE_APPLICATION_CREDENTIALS，若用 Vertex）。

### 第四步：启动应用

```bash
streamlit run app.py
```

---

## 四、风险与注意事项

| 项目 | 说明 |
|------|------|
| **工作目录** | 所有命令需在 **20260128** 下执行，否则相对路径 `./amah_vector_db`、`./medical_db`、`merged_data.json` 等会找不到。 |
| **merged_data.json 体量** | batch_build_db 会读取并写入 ChromaDB，数据量大时首次运行可能较久（审核中预估 2–3 小时含人工检查）。 |
| **expert_bulk_loader 输入** | 脚本通常从 `expert_map_data.json` 读入；确认该文件存在且格式正确。 |
| **网络与 API** | 若使用 Vertex/OpenAI/Anthropic，需网络可达且配额/计费已开通。 |

---

## 五、评价小结

1. **审核报告与新建文件（verify_prerequisites、requirements、E2E 测试、部署清单、中英文总结）** 与当前代码状态一致，**可直接作为交付与运行指南**。
2. **3 个阻塞项** 的修复方式正确；执行前务必先跑 **verify_prerequisites.py**，再按需执行初始化，避免重复或漏跑。
3. **ChromaDB 双路径**（medical_db vs amah_vector_db）已在上面说明，两脚本都执行可保证完整功能。
4. **Gemini 模型名** 建议列入后续小改进，不阻塞本次运行。
5. **结论：** 在确认 .env 至少有一个 LLM key、且按上述顺序执行「检查 → 依赖 → 初始化 → 启动」后，可以运行；建议先完成讨论与确认再执行第三步（数据初始化）。

---

*评价与讨论结束。确认后再执行第三步与第四步。*
