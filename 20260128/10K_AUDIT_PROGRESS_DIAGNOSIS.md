# 10k 匹配审计任务进度诊断说明

**日期：** 2026-01-28（依据对话摘要）  
**现象：** 全量 10k 任务已运行超过 6 小时，`matching_audit_results_10k.json` 与 `AMANI_TRAINING_10K_MATCHING_RESULTS_SUMMARY.md` 仍未生成/未更新。

---

## 1. 当前状态结论

| 检查项 | 结果 |
|--------|------|
| `matching_audit_results_10k.json` | **不存在**（脚本仅在**全部跑完后**才写入） |
| `run_10k_audit_log.txt` | **原脚本未生成**（原版无进度日志文件） |
| `AMANI_TRAINING_10K_MATCHING_RESULTS_SUMMARY.md` | 仍为占位符（“*运行后填写*”），说明脚本**尚未成功跑完** |
| Python 进程 | 存在（如 PID 38104 等），CPU 累计很低，可能长时间阻塞或单条极慢 |

**结论：** 任务要么仍在极慢推进（每条 `run_safe` 耗时数秒导致 10k 需数小时），要么已在某条上卡住/崩溃且无中间输出可查。

---

## 2. 原因分析

1. **只做“全量写完”**  
   脚本设计为：循环内只做 `run_one` 与内存列表累积，**全部 10,000 条处理完后**才调用 `write_results()` 写 JSON 和汇总 MD。因此只要未跑完，磁盘上不会有任何结果文件。

2. **单条耗时可能很大**  
   每条记录调用 `TrinityBridge.run_safe(original_inquiry)`，会走 L1 熵门 → L2 均等化 → L2.5 意图/策略 → L3 ChromaDB 检索与二次重排。若 ChromaDB 或上游组件慢，单条 2–5 秒很常见，则 10k × 3 秒 ≈ 8.3 小时，与“超过 6 小时仍未完成”一致。

3. **缺少进度可见性**  
   仅每 500 条在 stdout 打印一次，若任务在后台运行且未重定向 stdout，无法判断当前进度；且无日志文件，无法事后排查卡在第几条。

4. **无断点/部分结果**  
   若进程中途被杀或崩溃，已处理的结果全部丢失，只能重新跑。

---

## 3. 已采取的改进（脚本层面）

- **进度日志：** 在 `run_training_10k_matching_audit.py` 中增加 `run_10k_audit_log.txt`，每处理 100 条（可配置）写入一行：时间戳、已处理条数/总条数、已耗时（秒）。便于观察是否在推进、以及大致速度。
- **分批写盘：** 每处理满 N 条（如 2000）将当前 `results` 写入 `matching_audit_results_10k_partial.json`，正常结束时再写最终 `matching_audit_results_10k.json` 与汇总 MD；若中途中断，至少保留部分结果与进度。

重新运行或后续长时间任务时，可通过查看 `run_10k_audit_log.txt` 和 `matching_audit_results_10k_partial.json` 判断进度与原因。

---

## 4. 建议操作

1. **若需确认当前是否还在跑：**  
   查看任务管理器/`Get-Process python*`，确认对应 PID 是否仍存在；若有 `run_10k_audit_log.txt`（改进版脚本产生），看最后一行时间戳与条数是否在增加。

2. **若已确认卡死或希望重跑：**  
   结束当前 Python 进程后，使用**改进后的** `run_training_10k_matching_audit.py` 重新运行（可先用 `python run_training_10k_matching_audit.py 500` 做短测试），并观察 `run_10k_audit_log.txt` 与 `matching_audit_results_10k_partial.json` 的更新情况。

3. **若环境单条过慢：**  
   考虑先用 `python run_training_10k_matching_audit.py 1000` 或 2000 做子集测试并得到部分统计；或优化 ChromaDB/TrinityBridge 单次调用性能后再跑全量。

*End of Diagnosis*
