# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
对 amani_training_10k.json 中所有客户需求执行 USER_REQUEST_MATCHING_LOGIC_AUDIT 定义的匹配逻辑运行测试。
入口：TrinityBridge.run_safe(original_inquiry)；输出：每条结果 + 汇总报告。
"""
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# 路径（脚本在 20260128 下运行）
BASE = Path(__file__).resolve().parent
TRAINING_FILE = BASE / "amani_training_10k.json"
RESULTS_JSON = BASE / "matching_audit_results_10k.json"
SUMMARY_MD = BASE / "AMANI_TRAINING_10K_MATCHING_RESULTS_SUMMARY.md"
PROGRESS_LOG = BASE / "run_10k_audit_log.txt"
PARTIAL_JSON = BASE / "matching_audit_results_10k_partial.json"

# 进度日志与分批写盘间隔（便于诊断与恢复）
LOG_EVERY_N = 100
CHECKPOINT_EVERY_N = 2000


def load_training_data(limit: int = None) -> List[Dict[str, Any]]:
    """加载 amani_training_10k.json，可选 limit 条（用于快速测试）。"""
    with open(TRAINING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if limit is not None and limit > 0:
        data = data[:limit]
    return data


def run_one(bridge, record: Dict[str, Any]) -> Dict[str, Any]:
    """对单条记录执行 TrinityBridge.run_safe(original_inquiry)，返回紧凑结果。"""
    request_id = record.get("request_id", "")
    asset_category = record.get("asset_category", "")
    inquiry = record.get("original_inquiry", "")
    out = {
        "request_id": request_id,
        "asset_category": asset_category,
        "intercepted": True,
        "l1_passed": False,
        "d_effective": None,
        "variance": None,
        "agid_count": 0,
        "error_msg": None,
    }
    try:
        result = bridge.run_safe(inquiry or " ", top_k_agids=5)
        intercepted = result.get("intercepted", True)
        out["intercepted"] = intercepted
        out["l1_passed"] = not intercepted
        l1 = result.get("l1_sentinel") or {}
        out["d_effective"] = l1.get("d_effective")
        out["variance"] = l1.get("shannon_entropy_variance")
        if not intercepted:
            l3 = result.get("l3_nexus") or {}
            agids = l3.get("agids") or []
            out["agid_count"] = len(agids)
    except Exception as e:
        out["error_msg"] = str(e)[:500]
    return out


def _log_progress(log_path: Path, msg: str) -> None:
    """追加一行进度到 run_10k_audit_log.txt，立即刷新。"""
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
            f.flush()  # 立即刷新，确保进度可见
    except Exception:
        pass


def run_audit(limit: int = None) -> tuple:
    """
    加载训练数据，对每条 original_inquiry 执行 run_safe，返回 (results_list, stats_dict)。
    每 LOG_EVERY_N 条写入进度到 run_10k_audit_log.txt；每 CHECKPOINT_EVERY_N 条写 partial JSON。
    """
    records = load_training_data(limit=limit)
    try:
        from amani_trinity_bridge import TrinityBridge
    except Exception as e:
        print(f"Import TrinityBridge failed: {e}")
        sys.exit(1)
    bridge = TrinityBridge()
    results: List[Dict[str, Any]] = []
    start = time.time()
    total = len(records)
    _log_progress(PROGRESS_LOG, f"[start] total={total} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    for i, rec in enumerate(records):
        r = run_one(bridge, rec)
        results.append(r)
        n = i + 1
        elapsed = time.time() - start
        # 每条都记录到日志（便于诊断卡住的位置），但只显示前10条和之后每100条
        if n <= 10 or n % LOG_EVERY_N == 0:
            _log_progress(PROGRESS_LOG, f"[progress] {n}/{total} elapsed_sec={round(elapsed, 1)}")
        if n % 500 == 0:
            print(f"  Processed {n}/{total} ...")
            sys.stdout.flush()  # 立即刷新 stdout
        if n % CHECKPOINT_EVERY_N == 0:
            try:
                with open(PARTIAL_JSON, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
    elapsed = time.time() - start
    _log_progress(PROGRESS_LOG, f"[done] {total}/{total} elapsed_sec={round(elapsed, 1)}")
    # 统计
    total = len(results)
    intercepted = sum(1 for x in results if x["intercepted"])
    passed = total - intercepted
    by_cat: Dict[str, Dict[str, int]] = {}
    for x in results:
        c = x.get("asset_category") or "Unknown"
        if c not in by_cat:
            by_cat[c] = {"total": 0, "intercepted": 0, "passed": 0, "with_agids": 0}
        by_cat[c]["total"] += 1
        if x["intercepted"]:
            by_cat[c]["intercepted"] += 1
        else:
            by_cat[c]["passed"] += 1
            if (x.get("agid_count") or 0) > 0:
                by_cat[c]["with_agids"] += 1
    errors = [x for x in results if x.get("error_msg")]
    stats = {
        "total": total,
        "intercepted": intercepted,
        "passed_l1": passed,
        "with_agids": sum(1 for x in results if (x.get("agid_count") or 0) > 0),
        "errors": len(errors),
        "elapsed_seconds": round(elapsed, 2),
        "by_asset_category": by_cat,
    }
    return results, stats


def write_results(results: List[Dict[str, Any]], stats: Dict[str, Any]) -> None:
    """写入 matching_audit_results_10k.json 与 AMANI_TRAINING_10K_MATCHING_RESULTS_SUMMARY.md"""
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    # 汇总 Markdown
    lines = [
        "# A.M.A.N.I. 训练集 10k 客户需求 — 匹配逻辑运行测试结果汇总",
        "",
        "**Stamp:** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN",
        "**依据:** USER_REQUEST_MATCHING_LOGIC_AUDIT.md（用户诉求匹配逻辑审核）",
        "**入口:** TrinityBridge.run_safe(original_inquiry)；数据源: amani_training_10k.json",
        "**脚本:** run_training_10k_matching_audit.py",
        "",
        "---",
        "",
        "## 1. 总体统计",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| 总条数 | {stats['total']} |",
        f"| L1 通过（进入 L2/L3） | {stats['passed_l1']} |",
        f"| L1 拦截 | {stats['intercepted']} |",
        f"| 获得至少 1 个 AGID | {stats['with_agids']} |",
        f"| 运行异常（error_msg 非空） | {stats['errors']} |",
        f"| 总耗时（秒） | {stats['elapsed_seconds']} |",
        "",
        "---",
        "",
        "## 2. 按资产类别（asset_category）统计",
        "",
        "| 资产类别 | 总条数 | L1 拦截 | L1 通过 | 获得 AGID 数 |",
        "|----------|--------|--------|--------|--------------|",
    ]
    for cat, c in stats.get("by_asset_category", {}).items():
        lines.append(f"| {cat} | {c['total']} | {c['intercepted']} | {c['passed']} | {c['with_agids']} |")
    lines.extend([
        "",
        "---",
        "",
        "## 3. 结果文件",
        "",
        f"- **逐条结果（JSON）:** `matching_audit_results_10k.json`",
        f"- **本汇总:** `AMANI_TRAINING_10K_MATCHING_RESULTS_SUMMARY.md`",
        "",
        "---",
        "",
        "## 4. 说明",
        "",
        "- **L1 通过** = 未触发 StrategicInterceptError，即 variance ≤ 配置上限且 D ≤ 0.79。",
        "- **L1 拦截** = run_safe 返回 intercepted=True，无 L2/L3 匹配结果。",
        "- **获得 AGID** = L3 返回的 agids 数量 ≥ 1。",
        "",
        "*End of Summary*",
    ])
    with open(SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    limit = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        limit = int(sys.argv[1])
        print(f"Running with limit={limit}")
    else:
        print("Running full 10,000 records (this may take several minutes)...")
    print("Loading training data...")
    records = load_training_data(limit=limit)
    print(f"Loaded {len(records)} records. Running TrinityBridge.run_safe for each...")
    results, stats = run_audit(limit=limit)
    print("Writing results...")
    write_results(results, stats)
    print(f"Done. Results: {RESULTS_JSON}")
    print(f"Summary: {SUMMARY_MD}")
    print(f"Total: {stats['total']}, Passed L1: {stats['passed_l1']}, Intercepted: {stats['intercepted']}, Errors: {stats['errors']}, Elapsed: {stats['elapsed_seconds']}s")


if __name__ == "__main__":
    main()
