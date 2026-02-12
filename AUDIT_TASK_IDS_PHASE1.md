# AUDIT_TASK_IDS_PHASE1

## P0 (立即执行)
- `AUD-P0-001` 依赖清单修复：补齐 `requests/google-generativeai/tqdm/matplotlib/pydeck/fpdf/biopython/langchain-openai` 到依赖文件并锁定版本。
- `AUD-P0-002` 去重并收敛扩容脚本：处理 `blitz_expansion_v2.py` 与 `nano blitz_expansion_v2.py` 的重复入口，保留唯一生产脚本。
- `AUD-P0-003` 修复 `merged_data.json.py` 命名与逻辑错配：重命名为明确脚本名并修正输入文件提示一致性。

## P1 (高优先)
- `AUD-P1-004` 清理非标准临时资产：规范 `Mayo Internal Ref VERIFIED` 的命名与存放位置。
- `AUD-P1-005` 建立“唯一生产入口”清单：为 v2/v2_5/v4 系列脚本标记主入口，冻结非主路径执行。
- `AUD-P1-006` 新增静态依赖健康检查：在 CI/本地预检中加入 import smoke test。

## P2 (进入 Phase 2 前)
- `AUD-P2-007` 设计 Alpha 预测逻辑的偏置审计基准集（按国家/语言/疾病亚型分层）。
- `AUD-P2-008` 设计全球资源调度压测矩阵（多国家、多时区、多语言、并发负载）。
- `AUD-P2-009` 设计医疗隐私与传输审计基线（加密、密钥管理、日志脱敏、数据保留策略）。
