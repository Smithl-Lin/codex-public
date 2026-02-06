# MedicalReasoner / Orchestrator / BatchProcessQueue 方案与修改细节评估

**评估角色:** AII 与程序写作专家  
**日期:** 2026-01-28  
**范围:** medical_reasoner.py、Orchestrator、BatchProcessQueue 与 L2/L4 管线  

---

## 一、方案评估总览

| 项 | 方案要点 | 可行性 | 当前差距 | 已实施修改 |
|----|----------|--------|----------|------------|
| **1. MedicalReasoner 指令集** | 五层专用 System Prompt；AGID 识别；强制「资源匹配建议」 | ✅ 可行 | 无专用 Prompt；无 resource_matching_suggestion | ✅ 已加 AMANI_SYSTEM_PROMPT、resource_matching_suggestion、_call_endpoint 传 system_prompt |
| **2. Orchestrator 审计逻辑** | 主权审计；算力开销 + 合规得分；路径截断/强制脱敏 | ✅ 可行 | 原为透传；未读 amah_config 安全策略 | ✅ 已加 orchestrator_audit 配置、双重判定、路径截断与脱敏；StaircaseMappingLLM 经 Orchestrator |
| **3. BatchProcessQueue 异步** | 并发限制；与 TrinityBridge 反馈挂钩；L4 推理进度条 | ✅ 可行 | 无并发限制；无进度；无 L4 轮询接口 | ✅ 已加 max_concurrency、get_job_status、progress_callback；L4 提供 get_batch_job_status、set_batch_progress_callback |

---

## 二、逐项评估与修改细节

### 2.1 MedicalReasoner (MedGemma 27B) 指令集修改

**查看点结论：**
- **Prompt 模板：** 原实现无专用 System Prompt，仅向 endpoint 传 `input_text` 与 `l1_context`。
- **AGID 识别：** stub 与 endpoint 返回的 strategy 中虽有 `agid` 字段，但未要求模型输出与 A.M.A.N.I. 五层语义一致，也未强制「资源匹配建议」。

**修改动作（已实施）：**
1. **AMANI_SYSTEM_PROMPT**  
   - 常量：说明 A.M.A.N.I. 临床推理模块身份，要求输出 JSON 含 `strategy`、`intent_summary`、**resource_matching_suggestion**（必填）。  
   - `resource_matching_suggestion` 结构：`imaging`（如 MRI、CT）、`therapeutics`（药物/类别）、`pi_experts`（专家/专科），并注明使用 AGID 格式。

2. **MedicalReasoner.get_system_prompt()**  
   - 返回上述系统提示词，供 _call_endpoint 注入。

3. **_call_endpoint**  
   - 请求体增加 `system_prompt`，便于 MedGemma 服务端按 A.M.A.N.I. 规范生成。

4. **resource_matching_suggestion 强制**  
   - `reason()` 在调用 endpoint 后若缺少该字段，用 `_default_resource_suggestion(out)` 补全。  
   - `_stub_reason()` 始终返回 `resource_matching_suggestion`（默认含 imaging: ["MRI"] 等）。

5. **_default_resource_suggestion(out)**  
   - 当 MedGemma 未返回时提供默认 `{imaging, therapeutics, pi_experts}`，保证下游 L3 始终有「需调动的物理资产」类型信息。

**后续建议：**
- 若 MedGemma 实际 API 不支持 system_prompt 字段，可在服务端将 `AMANI_SYSTEM_PROMPT` 写死或通过专用 header/参数传入。
- 微调时可把 `AMANI_SYSTEM_PROMPT` 与 `resource_matching_suggestion` 示例写入 amani_finetuning_dataset，强化输出格式。

---

### 2.2 Orchestrator (Qwen/Gemini) 审计逻辑修改

**查看点结论：**
- **合并逻辑：** StaircaseMappingLLM.semantic_path 仅调用 MedicalReasoner.reason()，未经过 Orchestrator；Orchestrator 原为透传 stub。
- **幻觉/不合规：** 无校验；无 L1 高熵报警时的路径截断或脱敏。

**修改动作（已实施）：**
1. **amah_config.json 新增 orchestrator_audit**  
   - `path_truncation_on_high_entropy`: 是否在高熵时截断路径。  
   - `variance_limit_for_truncation`、`d_threshold_for_truncation`：与 L1 方差/D 阈值对齐。  
   - `compliance_score_min`、`reasoning_cost_max`：合规与算力上限。  
   - `force_desensitize_on_fail`：不达标时是否强制脱敏。

2. **Orchestrator 主权审计**  
   - 构造函数加载 `orchestrator_audit`（默认 amah_config.json）。  
   - `run(medical_output, mode, l1_context)`：  
     - 计算 **reasoning_cost**（stub：基于 strategy 长度；实装可改为 token/API 成本）。  
     - 计算 **compliance_score**（stub：基于是否含 resource_matching_suggestion 及 category 合规）。  
     - 若 `path_truncation_on_high_entropy` 为 true 且 L1 方差 > limit 或 D > threshold → **path_truncated**，仅保留 strategy 首项。  
     - 若 compliance_score < min 或 reasoning_cost > max 且 `force_desensitize_on_fail` → **desensitized**：截断 intent_summary、清空 resource_matching_suggestion 具体内容。  
   - 返回 payload + `reasoning_cost`、`compliance_score`、`path_truncated`、`desensitized`。

3. **StaircaseMappingLLM.semantic_path 经 Orchestrator**  
   - 在 reasoner.reason() 之后调用 `Orchestrator().run(out, mode="structured", l1_context=l1_context)`。  
   - 使用 audit.payload 作为 L2 输出，并将 `orchestrator_audit`（reasoning_cost、compliance_score、path_truncated、desensitized）写入 semantic_path，供 L3/L4 与审计日志使用。

**后续建议：**
- reasoning_cost 实装：对接 trinity_api_connector 的 token 统计或计费接口。  
- compliance_score 实装：接入 ComplianceGate 或规则引擎，对 resource_matching_suggestion 与 strategy 做策略合规检查。

---

### 2.3 BatchProcessQueue (批处理引擎) 异步逻辑

**查看点结论：**
- **并发：** 原为无界 list append，无并发控制。  
- **多模态/L4 影像桩：** enqueue 后无状态查询，UI 无法获知「推理中/进度」。  
- **与 TrinityBridge 反馈：** 无挂钩，L4 只能死等。

**修改动作（已实施）：**
1. **BatchProcessQueue**  
   - **max_concurrency**（默认 2）：构造函数参数，供实装时限制同时进行的 MedGemma 调用数。  
   - **_job_status**：每 job_id 对应 `{status, progress, message}`；enqueue 时写入 queued；process_all 中通过 _emit_progress 更新。  
   - **set_progress_callback(cb)**：`cb(job_id, progress_0_to_1, message)`，在 process_all 各阶段调用，便于 L4/TrinityBridge 实时展示进度。  
   - **get_job_status(job_id)**：供 L4 轮询进度与状态。  
   - **process_all**：stub 仍为同步循环，但对每个 job 调用 _emit_progress(0.1 → 0.5 → 1.0)，实装可改为异步 worker + 回调或队列消费。

2. **L4 接口（amani_interface_layer_v4）**  
   - **get_batch_job_status(job_id)**：调用同一单例 queue 的 get_job_status，供 UI 轮询「推理进度条」。  
   - **set_batch_progress_callback(callback)**：将 callback 设到 queue，实现 TrinityBridge/L4 反馈挂钩；App 在渲染批处理区域时设置，即可在 process_all 执行时收到 progress/message。

3. **TrinityBridge 挂钩说明**  
   - 当前 run/run_safe 为单条输入管线，不直接驱动 BatchProcessQueue。批处理由 L4 上传触发 enqueue，后台或定时 process_all 消费。  
   - 挂钩方式：在 App 或 L4 初始化时 `set_batch_progress_callback(cb)`，cb 内更新 Streamlit 状态（如 st.progress + st.caption），即可在「深度推理时」显示进度条而非死等。

**后续建议：**
- 实装 process_all：用线程池或 asyncio 限制 max_concurrency 路并发调用 MedGemma，每路完成时 _emit_progress(job_id, 1.0, "Done")。  
- Streamlit：对已知 job_id 用 st.empty() + 轮询 get_batch_job_status 刷新进度条，或使用 st.session_state 配合 progress_callback 更新。

---

## 三、涉及文件清单

| 文件 | 修改内容 |
|------|----------|
| medical_reasoner.py | AMANI_SYSTEM_PROMPT；MedicalReasoner.get_system_prompt、reason/resource_matching_suggestion；_default_resource_suggestion；Orchestrator 主权审计（config、reasoning_cost、compliance、截断/脱敏）；BatchProcessQueue max_concurrency、_job_status、progress_callback、get_job_status、_emit_progress |
| amah_config.json | orchestrator_audit 段 |
| amani_trinity_bridge.py | StaircaseMappingLLM.semantic_path 经 Orchestrator.run；输出增加 resource_matching_suggestion、orchestrator_audit |
| amani_interface_layer_v4.py | _get_batch_queue；get_batch_job_status；set_batch_progress_callback |

---

## 四、结论与建议

- **方案 1（MedicalReasoner 指令集）：** 已落实 A.M.A.N.I. 专用系统提示词与「资源匹配建议」强制字段，MedGemma 端需支持 system_prompt 或等价注入。  
- **方案 2（Orchestrator 审计）：** 已落实主权审计、算力/合规双重判定及基于 amah_config 的路径截断与强制脱敏；后续可接真实 cost 与合规规则。  
- **方案 3（BatchProcessQueue 异步）：** 已落实并发上限、进度状态与 L4 轮询/回调挂钩；UI 可通过 get_batch_job_status 与 set_batch_progress_callback 实现「推理进度条」，实装时在 process_all 内接入真实 MedGemma 调用与并发控制即可。

以上修改保持与现有五层架构兼容，并可直接用于后续 MedGemma 27B 与编排层实装与联调。
