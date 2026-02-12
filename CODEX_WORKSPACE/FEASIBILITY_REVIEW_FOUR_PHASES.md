# 四阶段修改策略 — 可行性结论与修改建议

**角色:** AI 专家 + 医学专家  
**结论:** 策略整体可行，建议在以下 3 点做小幅调整后执行，其余按原方案落地。

---

## 一、可行性结论（简要）

| 阶段 | 结论 | 说明 |
|------|------|------|
| 第一阶段 环境硬化与安全治理 | ✅ 可行 | .env 已存在（20260128/.env）；需新增 config 模块并统一读环境变量；.gitignore 需新建（当前无） |
| 第二阶段 逻辑中枢归拢 | ✅ 可行 | 需澄清：无「execute_global_match.py」文件，仅有 amani_core_v4.AMANICoreOrchestrator.execute_global_match；App 改为调用 TrinityBridge.run_safe 并映射结果到现有 UI |
| 第三阶段 资产与物理路径硬化 | ✅ 可行 | ChromaDB 已有 mayo_clinic_trials / expert_map_global；需定义「物理节点清单」格式（建议用 expert_map + hospital_center_assets 生成） |
| 第四阶段 MedGemma 适配 | ✅ 可行（预留为主） | 当前无 MedGemma 部署；建议先建 MedicalReasoner/Orchestrator 角色与配置桩，Endpoint 由配置或环境变量注入，便于后续接入 |

---

## 二、修改建议（讨论后执行）

### 建议 1：第二阶段「废弃冗余入口」的精确范围

- **原文：** 停用所有零散的独立执行脚本（如 execute_global_match.py）。
- **现状：** 仓库中不存在 `execute_global_match.py`。存在的是：
  - `amani_core_v4.AMANICoreOrchestrator.execute_global_match`（方法）
  - 调用方：`run_single_profile.py`、`test_amani_v4_full_loop.py`
- **建议：**
  - 不删除 `execute_global_match` 方法，保留为「非主入口」的兼容路径（例如后台或测试用）。
  - **主入口**统一为：App（及任何对外交互）仅调用 `TrinityBridge.run_safe`。
  - 在 `TrinityBridge.run_safe` 内部，如需复用原有「学科路由 + D + AGID」逻辑，可从 `amani_core_v4` 或现有 `get_strategic_routing` 中抽取并封装，而不是保留多处并列入口。
- **执行时：** App 改为调用 `TrinityBridge.run_safe(patient_input)`，将返回的 `l1_sentinel` / `l2_2_5_semantic_path` / `l3_nexus` / `l4_multimodal` 映射为当前 UI 的 dept、D、AGID、steps、experts、影子账单；若 `intercepted=True` 则展示拦截态。

### 建议 2：第二阶段「整合 Centurion 门控」的插入方式

- **原文：** 在 TrinityBridge 内部插入 AMAHCenturionInjector 的前置检查，确保所有请求先通过 L1 熵值检测（D≤0.79）和 L2 脉冲监测。
- **现状：** TrinityBridge 已有 L1（ECNNSentinel）；Centurion 的 L2 包含 Lifecycle_Pulse_Monitor（12h 脉冲扫描）。
- **建议：**
  - **L1：** 保持现有逻辑，TrinityBridge 内已有，不重复。
  - **L2 脉冲：** 在 `TrinityBridge.run()` 内，当 L1 通过且 D≤0.79 时，**可选**调用 `AMAHCenturionInjector.get_latest_snapshot(0.79)` 一次，将得到的 L2 资产摘要（如 component 数量）注入到上下文中，供 StaircaseMappingLLM 或后续 L3 使用；若 Centurion 未初始化或调用失败，则降级为仅用当前 Trinity L2/L3，不阻塞主流程。
  - 不将「脉冲监测」设为硬性前置阻塞（避免 12h 周期导致请求被拒），仅作「有则 enrichment，无则跳过」。

### 建议 3：第三阶段「物理节点清单」与 auto_register 的数据源

- **原文：** NexusRouter 增加 auto_register，启动时自动扫描物理节点清单，完成 AGID→物理 Endpoint 的映射。
- **现状：** 无单独「物理节点清单」文件；有 expert_map_data.json、hospital_center_assets.json 等。
- **建议：**
  - 定义**物理节点清单**为：从现有资产中导出「可解析为物理节点」的条目（如 id/agid、region、endpoint 占位符）。
  - **实现方式：**  
    - 新增 `physical_node_registry.json`（或由脚本从 expert_map_data + hospital_center_assets 生成），结构例如：`[{ "agid_or_id": "...", "region": "NA", "endpoint": "https://..." 或 "" }]`。  
    - `NexusRouter.auto_register(registry_path)`：启动时加载该文件，对每条调用 `register_physical_mapping(agid, node_id, region, endpoint)`；若无 endpoint 则用占位或空，后续由配置或管理接口补全。
  - 这样既满足「自动扫描并注册」，又避免与现有资产表结构强耦合。

### 建议 4：第四阶段 MedGemma 的「未部署」处理

- **原文：** MedicalReasoner 的 Endpoint 强制指向本地或 Vertex 上的 MedGemma。
- **现状：** 项目内尚未接入 MedGemma。
- **建议：**
  - **Endpoint 可配置化：** 在 amah_config.json 或 .env 中增加 `MEDGEMMA_ENDPOINT`（或 `MEDICAL_REASONER_ENDPOINT`），若为空则 MedicalReasoner 走 **stub**：返回与当前 StaircaseMappingLLM 规则一致的结构化结果，不报错。
  - 这样：逻辑上「所有请求经 MedicalReasoner」，实际未部署 MedGemma 时仍可运行；部署后仅需配置 Endpoint 即可切换。

---

## 三、执行顺序与依赖（建议）

1. **第一阶段**：新建/更新 .env、新建 config 模块、所有 Python 改为通过 config 读凭证、.gitignore 加入 .env。  
2. **第二阶段**：App 改为仅调用 TrinityBridge.run_safe；结果映射到现有 UI；TrinityBridge 内 L1 通过且 D≤0.79 时可选调用 Centurion.get_latest_snapshot 做 enrichment；保留 execute_global_match 为兼容入口。  
3. **第三阶段**：L2→ChromaDB 全量同步脚本；GNNAssetAnchor 改为从 ChromaDB 查询；定义 physical_node_registry 与 NexusRouter.auto_register。  
4. **第四阶段**：StaircaseMappingLLM 接入 MedicalReasoner（可配置 Endpoint + stub）；Orchestrator 角色；L4 影像上传桩与 Batch_Process 队列桩；配置 finetune_version。

---

## 四、请您确认

- 若同意上述 4 条建议，我将按「四阶段 + 建议」直接执行实现。  
- 若希望调整某条（例如 Centurion 必须硬性前置、或物理节点清单格式），请指出，我们按您的偏好改后再执行。

*End of Feasibility Review*
