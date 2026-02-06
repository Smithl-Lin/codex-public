# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
Async 10k audit runner with concurrency + rate limiting.
Uses AsyncLimiter (pip install aiolimiter) to avoid TPM spikes.
"""
import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from aiolimiter import AsyncLimiter

from run_training_10k_matching_audit import (
    load_training_data,
    run_one,
    write_results,
    RESULTS_JSON,
    SUMMARY_MD,
    LOG_EVERY_N,
    CHECKPOINT_EVERY_N,
)

BASE = Path(__file__).resolve().parent
PROGRESS_LOG = BASE / "run_10k_audit_async_log.txt"
PARTIAL_JSON = BASE / "matching_audit_results_10k_partial_async.json"

# 1) Rate gate: 80 requests per 60 seconds
limiter = AsyncLimiter(80, 60)
# 2) Concurrency gate: at most 3 in-flight requests
semaphore = asyncio.Semaphore(3)
# 3) Batch size: 20-50 items per group
BATCH_SIZE = 50


def _log_progress(msg: str) -> None:
    try:
        with open(PROGRESS_LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
            f.flush()
    except Exception:
        pass


def _build_stats(results: List[Dict[str, Any]], elapsed: float) -> Dict[str, Any]:
    total = len(results)
    intercepted = sum(1 for x in results if x.get("intercepted"))
    passed = total - intercepted
    by_cat: Dict[str, Dict[str, int]] = {}
    for x in results:
        c = x.get("asset_category") or "Unknown"
        if c not in by_cat:
            by_cat[c] = {"total": 0, "intercepted": 0, "passed": 0, "with_agids": 0}
        by_cat[c]["total"] += 1
        if x.get("intercepted"):
            by_cat[c]["intercepted"] += 1
        else:
            by_cat[c]["passed"] += 1
            if (x.get("agid_count") or 0) > 0:
                by_cat[c]["with_agids"] += 1
    errors = [x for x in results if x.get("error_msg")]
    return {
        "total": total,
        "intercepted": intercepted,
        "passed_l1": passed,
        "with_agids": sum(1 for x in results if (x.get("agid_count") or 0) > 0),
        "errors": len(errors),
        "elapsed_seconds": round(elapsed, 2),
        "by_asset_category": by_cat,
    }


async def _process_one(
    idx: int,
    record: Dict[str, Any],
    bridge,
    max_retries: int = 3,
) -> Tuple[int, Dict[str, Any]]:
    async with limiter:
        for attempt in range(max_retries):
            try:
                result = await asyncio.to_thread(run_one, bridge, record)
                return idx, result
            except Exception as e:
                msg = str(e)
                if "RateLimit" in msg or "429" in msg:
                    await asyncio.sleep(min(10, 2 ** attempt))
                    continue
                return idx, {
                    "request_id": record.get("request_id", ""),
                    "asset_category": record.get("asset_category", ""),
                    "intercepted": True,
                    "l1_passed": False,
                    "d_effective": None,
                    "variance": None,
                    "agid_count": 0,
                    "error_msg": msg[:500],
                }
        return idx, {
            "request_id": record.get("request_id", ""),
            "asset_category": record.get("asset_category", ""),
            "intercepted": True,
            "l1_passed": False,
            "d_effective": None,
            "variance": None,
            "agid_count": 0,
            "error_msg": "RateLimit retries exhausted",
        }


async def _process_batch(
    batch: List[Tuple[int, Dict[str, Any]]],
    bridge,
) -> List[Tuple[int, Dict[str, Any]]]:
    out: List[Tuple[int, Dict[str, Any]]] = []
    for idx, record in batch:
        out.append(await _process_one(idx, record, bridge))
    return out


async def main():
    limit = None
    records = load_training_data(limit=limit)
    total = len(records)
    _log_progress(f"[start] total={total} at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    from amani_trinity_bridge import TrinityBridge
    workers = max(1, min(3, total))
    results: List[Dict[str, Any]] = [None] * total  # type: ignore
    queue: asyncio.Queue = asyncio.Queue()
    batch: List[Tuple[int, Dict[str, Any]]] = []
    for i, rec in enumerate(records):
        batch.append((i, rec))
        if len(batch) >= BATCH_SIZE:
            queue.put_nowait(batch)
            batch = []
    if batch:
        queue.put_nowait(batch)

    progress_lock = asyncio.Lock()
    completed = 0
    start = time.time()

    async def worker_loop(worker_id: int) -> None:
        nonlocal completed
        bridge = TrinityBridge()
        while True:
            item = await queue.get()
            if item is None:
                queue.task_done()
                break
            batch_items = item
            async with semaphore:
                batch_results = await _process_batch(batch_items, bridge)
            for i, out in batch_results:
                results[i] = out
                async with progress_lock:
                    completed += 1
                    n = completed
                    elapsed = time.time() - start
                    if n <= 10 or n % LOG_EVERY_N == 0:
                        _log_progress(f"[progress] {n}/{total} elapsed_sec={round(elapsed, 1)}")
                    if n % CHECKPOINT_EVERY_N == 0:
                        try:
                            with open(PARTIAL_JSON, "w", encoding="utf-8") as f:
                                json.dump(results, f, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
            queue.task_done()

    tasks = [asyncio.create_task(worker_loop(i)) for i in range(workers)]
    await queue.join()
    for _ in tasks:
        queue.put_nowait(None)
    await asyncio.gather(*tasks)

    elapsed = time.time() - start
    _log_progress(f"[done] {total}/{total} elapsed_sec={round(elapsed, 1)}")
    stats = _build_stats(results, elapsed)
    write_results(results, stats)
    print(f"Done. Results: {RESULTS_JSON}")
    print(f"Summary: {SUMMARY_MD}")
    print(f"Total: {stats['total']}, Passed L1: {stats['passed_l1']}, Intercepted: {stats['intercepted']}, Errors: {stats['errors']}, Elapsed: {stats['elapsed_seconds']}s")


if __name__ == "__main__":
    asyncio.run(main())
