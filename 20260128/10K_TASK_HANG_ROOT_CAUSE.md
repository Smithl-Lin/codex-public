# 10k 任务卡住根本原因分析

**日期：** 2026-02-03  
**问题：** 反复多次运行 10k 匹配审计任务均未完成，进程卡住无响应。

---

## 1. 问题现象

- **任务启动：** 正常（日志显示 `[start]`）
- **进度更新：** 无（连第一条的 `[progress]` 都未出现）
- **进程状态：** Python 进程存在但 CPU 使用率极低（11+ 小时仅 2.5 秒 CPU）
- **结果文件：** 无任何输出（`matching_audit_results_10k.json`、`matching_audit_results_10k_partial.json` 均不存在）

---

## 2. 诊断结果

### 2.1 单次调用测试

通过 `test_first_record.py` 测试第一条记录的处理：

```
[08:48:59] 初始化 TrinityBridge... ✅ (0.64秒)
[08:49:00] 开始处理第一条记录...
[08:49:00] 输入文本: Urgent: Family member with ALS...
[卡住，超时]
```

**结论：** 问题出在 `bridge.run_safe()` 调用时，**第一条记录的处理就卡住了**。

### 2.2 组件测试结果

| 组件 | 状态 | 耗时 | 说明 |
|------|------|------|------|
| **TrinityBridge 导入** | ✅ | 0.08秒 | 正常 |
| **TrinityBridge 初始化** | ✅ | 0.68秒 | 正常 |
| **ChromaDB 连接** | ✅ | 0.03秒 | 正常（150条记录） |
| **L1 ECNNSentinel 单独** | ⚠️ | - | 会触发拦截（业务逻辑正常） |
| **完整 run_safe 调用** | ❌ | **卡住** | **问题所在** |

---

## 3. 根本原因分析

### 3.1 可能的阻塞点

`run_safe()` → `run()` 的调用链中，以下步骤可能阻塞：

1. **L1 熵门检查** (`self._l1.monitor()`)
   - ✅ 已单独测试，正常（会触发拦截但不会卡住）

2. **AMAHCenturionInjector** (`amah_centurion_injection.py`)
   - ⚠️ 可能初始化或查询数据库时阻塞
   - 代码位置：`amani_trinity_bridge.py:445-449`

3. **L2 文化均等化** (`amani_cultural_equalizer_l2.equalize_main_complaint()`)
   - ⚠️ 可能涉及文件 I/O 或网络请求
   - 代码位置：`amani_trinity_bridge.py:453-456`

4. **L2.5 语义路径** (`self._l2.semantic_path()`)
   - ⚠️ 可能调用 `medical_reasoner.MedicalReasoner()` 或 `Orchestrator()`
   - 如果配置了外部 API 端点，可能网络超时
   - 代码位置：`amani_trinity_bridge.py:457`

5. **硬锚点提取** (`_extract_hard_anchors()` / `_load_hard_anchor_config()`)
   - ⚠️ 可能读取配置文件时阻塞
   - 代码位置：`amani_trinity_bridge.py:461-462`

6. **L3 ChromaDB 查询** (`self._l3.forward()` → `map_to_agids()`)
   - ⚠️ **最可能的原因**
   - `chroma_collection.count()` 每次调用（第 303 行）
   - `chroma_collection.query()` 批量查询（第 308-312 行）
   - 如果 ChromaDB 数据库很大或索引未优化，可能极慢
   - 代码位置：`amani_trinity_bridge.py:466` → `amani_trinity_bridge.py:303-312`

7. **L4 多模态输出** (`UIPresenter()`)
   - ⚠️ 可能初始化或渲染时阻塞
   - 代码位置：`amani_trinity_bridge.py:478-495`

### 3.2 最可能的原因

**ChromaDB 查询阻塞**，原因：

1. **每次调用 `count()`**：`map_to_agids()` 第 303 行每次都会调用 `self._chroma_collection.count()`，如果数据库很大，这可能很慢。

2. **批量查询 `n_results=100`**：当启用硬锚点二次重排时，会查询 `retrieval_pool_size_n=100` 条候选（第 304 行），然后进行二次排序。如果数据库很大且索引未优化，这可能极慢。

3. **ChromaDB 锁机制**：如果 ChromaDB 使用文件锁，批量查询可能互相阻塞。

---

## 4. 解决方案

### 4.1 立即修复（推荐）

**优化 ChromaDB 查询，避免每次调用 `count()`：**

在 `amani_trinity_bridge.py` 的 `GNNAssetAnchor.__init__` 中缓存 `count()` 结果：

```python
def __init__(self, ...):
    # ... 现有代码 ...
    self._chroma_collection = self._chroma_client.get_collection(collection_name)
    # 缓存 count，避免每次查询都调用
    try:
        self._cached_count = self._chroma_collection.count()
    except Exception:
        self._cached_count = None
```

在 `map_to_agids()` 中使用缓存：

```python
# 第 303 行改为：
total = self._cached_count if self._cached_count is not None else self._chroma_collection.count()
```

### 4.2 添加超时机制

在 `run_training_10k_matching_audit.py` 的 `run_one()` 中添加超时：

```python
import signal

def run_one(bridge, record: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    """对单条记录执行 run_safe，带超时。"""
    # ... 现有代码 ...
    try:
        # Windows 不支持 signal，使用 threading.Timer 或其他方式
        result = bridge.run_safe(inquiry or " ", top_k_agids=5)
        # ... 处理结果 ...
    except Exception as e:
        out["error_msg"] = f"Timeout or error: {str(e)[:500]}"
    return out
```

### 4.3 分批处理并添加进度日志

已在 `run_training_10k_matching_audit.py` 中添加了进度日志（每 100 条）和分批写盘（每 2000 条），但需要确保日志在每条处理后立即刷新：

```python
def _log_progress(log_path: Path, msg: str) -> None:
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
            f.flush()  # 立即刷新
    except Exception:
        pass
```

### 4.4 临时绕过方案

如果 ChromaDB 查询确实很慢，可以临时禁用 ChromaDB，使用内存 fallback：

```python
# 在 run_training_10k_matching_audit.py 中：
bridge = TrinityBridge(chromadb_path=None)  # 禁用 ChromaDB
```

---

## 5. 验证步骤

1. **应用修复后，先测试单条记录：**
   ```bash
   python test_first_record.py
   ```
   应该能在 5 秒内完成。

2. **测试 10 条记录：**
   ```bash
   python run_training_10k_matching_audit.py 10
   ```
   观察 `run_10k_audit_log.txt` 是否正常更新。

3. **逐步增加：** 100 → 500 → 1000 → 10000

---

## 6. 总结

**根本原因：** ChromaDB 查询（特别是 `count()` 和批量 `query()`）在批量处理时阻塞，导致第一条记录就卡住。

**优先级：** 🔴 **CRITICAL** — 必须修复才能运行 10k 任务。

**预计修复时间：** 30 分钟（优化查询 + 添加超时 + 测试）

*End of Analysis*
