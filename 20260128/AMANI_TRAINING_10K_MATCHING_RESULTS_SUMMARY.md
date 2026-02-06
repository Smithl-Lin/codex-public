# A.M.A.N.I. 训练集 10k 客户需求 — 匹配逻辑运行测试结果汇总

**Stamp:** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
**依据:** USER_REQUEST_MATCHING_LOGIC_AUDIT.md（用户诉求匹配逻辑审核）
**入口:** TrinityBridge.run_safe(original_inquiry)；数据源: amani_training_10k.json
**脚本:** run_training_10k_matching_audit.py

---

## 1. 总体统计

| 指标 | 数值 |
|------|------|
| 总条数 | 10000 |
| L1 通过（进入 L2/L3） | 0 |
| L1 拦截 | 10000 |
| 获得至少 1 个 AGID | 0 |
| 运行异常（error_msg 非空） | 0 |
| 总耗时（秒） | 24017.35 |

---

## 2. 按资产类别（asset_category）统计

| 资产类别 | 总条数 | L1 拦截 | L1 通过 | 获得 AGID 数 |
|----------|--------|--------|--------|--------------|
| BCI | 2500 | 2500 | 0 | 0 |
| Gene_Therapy | 2500 | 2500 | 0 | 0 |
| Stem_Cell | 2500 | 2500 | 0 | 0 |
| Clinical_Trial | 2500 | 2500 | 0 | 0 |

---

## 3. 结果文件

- **逐条结果（JSON）:** `matching_audit_results_10k.json`
- **本汇总:** `AMANI_TRAINING_10K_MATCHING_RESULTS_SUMMARY.md`

---

## 4. 说明

- **L1 通过** = 未触发 StrategicInterceptError，即 variance ≤ 配置上限且 D ≤ 0.79。
- **L1 拦截** = run_safe 返回 intercepted=True，无 L2/L3 匹配结果。
- **获得 AGID** = L3 返回的 agids 数量 ≥ 1。

*End of Summary*