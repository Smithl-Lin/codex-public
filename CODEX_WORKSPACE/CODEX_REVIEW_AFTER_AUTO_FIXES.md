# Codex Review: Post–AUTO Fix Verification and Remaining Recommendations

**Date:** 2026-01-28  
**Mode:** Codex (audit of AUTO-model fixes)  
**Scope:** A.M.A.N.I. V4/V5 priority fixes — entry closure, Centurion blocking, L3 sovereignty, L3 fallback transparency.

---

## 1. Fix Verification (AUTO-Completed)

### 1.1 ✅ Unified Entry Point and L1 Gate Closure

| Item | Status | Evidence |
|------|--------|----------|
| app_v4.py routing | ✅ | `get_strategic_routing()` calls `TrinityBridge.run_safe()` and `_bridge_result_to_routing()`; no alternate routing path. |
| app.py routing | ✅ | `get_strategic_routing()` calls `TrinityBridge.run_safe()` and `_bridge_result_to_ui()`; button handler also uses `bridge.run_safe()`. |
| Bypass risk | ✅ | Old direct routing logic removed; all UI paths go through L1 via `run_safe()`. |

**Codex verdict:** Entry closure is satisfied. No bypass found.

---

### 1.2 ✅ Centurion Blocking Mitigation

| Item | Status | Evidence |
|------|--------|----------|
| Config-driven enable | ✅ | `amani_trinity_bridge.run()` reads `amah_config.json` → `centurion_injection.enabled` (default false). |
| Timeout in thread | ✅ | When enabled, Centurion runs in a daemon thread with `join(timeout=_cent_timeout)`; `timeout_seconds` from config (default 5). |
| Graceful skip | ✅ | If disabled or timeout/exception: `centurion_snapshot = None`; pipeline continues without blocking. |
| amah_config.json | ✅ | `20260128/amah_config.json` contains `centurion_injection: { "enabled": false, "timeout_seconds": 5 }`. |

**Codex verdict:** Centurion no longer blocks the main thread; 10k task can complete with Centurion disabled or under timeout.

---

### 1.3 ✅ L3 Registry Single-Point Mitigation

| Item | Status | Evidence |
|------|--------|----------|
| Singleton router | ✅ | `amani_nexus_layer_v3.get_default_router(registry_path)` creates/returns a single NexusRouter and optionally `auto_register(registry_path)`. |
| App-side load | ✅ | `app.py` and `app_v4.py` call `get_default_router(os.path.join(base, "physical_node_registry.json"))` at start of `get_strategic_routing()`. |
| First-use load | ✅ | Registry is loaded on first routing request when file exists; no dependency on a separate sync process run in the same session. |

**Codex verdict:** Registry single-point risk is reduced; app can load `physical_node_registry.json` at first use. For production, still recommend running `sync_l2_to_chromadb` so the file is present and up to date.

---

### 1.4 ✅ L3 Fallback Transparency (No Silent Degradation)

| Item | Status | Evidence |
|------|--------|----------|
| Origin flag | ✅ | `GNNAssetAnchor.forward()` sets `l3_origin: "chromadb"` when `_chroma_collection` is set, else `"fallback"`. |
| Audit visibility | ✅ | Downstream and auditors can check `result["l3_nexus"]["l3_origin"]` to see whether AGIDs came from ChromaDB or in-memory fallback. |

**Codex verdict:** L3 no longer silently degrades; fallback is explicit and auditable.

---

## 2. Remaining Recommendations (Codex)

### 2.1 L2.5 and Orchestrator

- **Strengthen L2.5:** Ensure StaircaseMappingLLM / MedicalReasoner path is the only semantic path and that L2.5 enrichment (e.g. Shadow Quote) is consistently applied before L3.
- **Orchestrator audit:** Confirm `medical_reasoner.Orchestrator` uses `amah_config.json` (e.g. `orchestrator_audit`) for cost/compliance thresholds and path truncation.

### 2.2 Protocol and Observability

- **Protocol monitor:** Add optional audit log (e.g. D, variance, l3_origin, intercepted) per request for sovereignty compliance (D ≤ 0.79) and debugging.
- **Variance config:** Document or wire `trinity_audit_gate.variance_limit_numeric` (e.g. 0.005) in one place; currently bridge reads it when present in config.

### 2.3 Concurrency and Production

- **Concurrency guard:** For high-throughput or 10k-style batch runs, consider rate limiting or connection pooling for ChromaDB and external services to avoid thundering herd.
- **Deployment:** Ensure `amah_config.json`, `physical_node_registry.json`, and ChromaDB path are present and correct in the deployment environment; run `sync_l2_to_chromadb` as part of deploy or first-start.

### 2.4 Optional Hardening

- **L3 fallback warning:** When `l3_origin == "fallback"`, optionally log a warning or set a metric so ops can alert on missing or unreachable ChromaDB.
- **Centurion re-enable:** When re-enabling Centurion (`centurion_injection.enabled: true`), keep `timeout_seconds` low (e.g. 5) and monitor for slow `get_latest_snapshot` calls.

---

## 3. Summary

| Fix | AUTO Status | Codex Verification |
|-----|-------------|--------------------|
| Entry + L1 closure | Done | ✅ Verified |
| Centurion blocking | Done | ✅ Verified |
| L3 registry single-point | Done | ✅ Verified |
| L3 fallback transparency | Done | ✅ Verified |

All four AUTO-delivered fixes are verified. The remaining four items have been implemented:

| Fix | Status | Implementation |
|-----|--------|----------------|
| **L2.5 authority** | Done | `amah_config.json`: `l2_5_authority`, `orchestrator_audit`; StaircaseMappingLLM docstring notes single semantic path. |
| **Protocol audit** | Done | `protocol_audit.enabled` / `log_path`; `run_safe` appends one line per request (ts, intercepted, d_effective, variance, l3_origin) to `sovereignty_audit.log`. |
| **Concurrency guard** | Done | `concurrency_guard.enabled` / `max_concurrent_bridge_calls`; `run_safe` uses module-level semaphore to limit concurrent bridge calls. |
| **Deployment critical** | Done | `verify_prerequisites.check_deployment_critical()`: amah_config sections, physical_node_registry.json, ChromaDB path; suggests `sync_l2_to_chromadb` if registry missing. |

No additional code changes required for this review cycle.
