# AMANI Unified Vision (Chronological Reconstruction + Blueprint)

## [Executive Summary]
AMANI is a deterministic, compliance-aware AI orchestration hub that maps patient intent to verifiable global medical assets, then outputs executable care-routing and value decisions.

## [Product Evolution]
### A. Timeline Reconstruction (by in-doc date markers + file modified time)
1. 2026-01-11 to 2026-01-17 (concept seed)
- Core narrative appears as "global medical asset scheduling" and "Nasdaq of Medical Resources".
- Early pillars: Trinity-Audit, resource routing, shadow billing, patent moat, PI fingerprint.
- Representative sources:
  - `...Medical Res\0111 work log.docx`
  - `...Medical Res\0111 策略.docx`
  - `...Medical Res\0117 商业逻辑.docx`
  - `...Medical Res\0117 Patent 1-8.docx`

2. 2026-01-18 to 2026-01-21 (dataset and demand mapping)
- "Final" dataset naming emerges (100-case/2k/100k variants), with multilingual and region-labeled assets.
- Product direction expands from pure routing to C-end decision navigation (China/US user journeys).
- Representative sources:
  - `...Medical Res\0101 阶段性结果\...\AMANI_MASTER_ASSET_DB_vFinal.csv`
  - `...Medical Res\0121 中美 C 端医疗需求深度调研报告与战略映射.docx`

3. 2026-01-28 to 2026-01-30 (V4 architecture lock)
- V4 formalized into 5-layer system (L1/L2/L2.5/L3/L4), explicitly introducing commercial-clinical value layer (L2.5).
- Compliance language becomes explicit: HIPAA/GDPR/PIPL gateway; global routing and multilingual interface.
- Representative sources:
  - `...Medical Res\01-28 核心战略点AMANI.docx`
  - `...Medical Res\0130 AMANI V4.0 Business Architecture Whitepaper.docx`
  - `...Medical Res\0130 AMANI V4.0 Global Sovereign Medical AI Architecture.docx`
  - `...Medical Res\0130 AMANI V4 Demo.docx`

4. 2026-02-01 and later execution logs (implementation reality)
- Engineering notes converge on TrinityBridge as runtime entry, NexusRouter registry sync, configurable orchestration, top-100 hospital onboarding.
- Implementation reports identify gaps: compliance gate mostly framework-level, MedGemma path not fully productionized, dual-path logic still present.
- Representative sources:
  - `...Medical Res\0201 working log and 策略.docx`
  - `...Medical Res\0130 Cursor\CURSOR_AMANI_WORK_SUMMARY.md`
  - `AMANI Project\20260128\SYSTEM_AUDIT_REPORT_AMANI.md`

### B. Inheritance / Deprecation Resolution
- Rule applied: when conflict exists, newer dated sources supersede older statements.
- Superseded logic:
  - "Platform as static directory/search" -> replaced by V4 five-layer deterministic orchestration.
  - "Single-layer commercial pitch" -> replaced by L2.5 value engine integrated with L1 precision gates and L3 compliance routing.
  - "Concept-only global claims" -> replaced by code-linked AGID/Nexus/registry workflow.

## [The Blueprint]
### 1) Final Product Positioning
- Category: Sovereign Medical Resource Orchestration Platform.
- Core promise:
  - lower mismatch latency (finding the right resource faster),
  - increase high-confidence match rate (deterministic gate + routing),
  - preserve cross-region compliance constraints.

### 2) Strategic OKRs (3-5)
1. Match Precision OKR
- Keep high-confidence routing under deterministic policy gates (D-threshold + consensus variance policy).

2. Operational Latency OKR
- Cut time from user intent to physically anchorable asset recommendation through unified entry and route execution.

3. Compliance OKR
- Enforce auditable region-aware handling (HIPAA/GDPR/PIPL profiles), including consent and traceability.

4. Asset Coverage OKR
- Maintain continuously synchronized, quality-scored global asset graph (trials, PI, hospitals, endpoints).

5. Commercialization OKR
- Convert routing outcomes into measurable value pathways (subscription + success fee + institutional workflows).

### 3) Functional Panorama (System Map)
1. L1 Sovereign Protocol Layer
- intent-density checks, precision/intercept gates, consensus policy checks.

2. L2 Asset Intelligence Layer
- therapeutic assets, PI registry, lifecycle pulse, disease-path context.

3. L2.5 Value Layer
- shadow quote/value routing, journey planning, scarcity and impact weighting.

4. L3 Global Nexus Layer
- AGID to physical node anchoring, regional routing, compliance gateway.

5. L4 Interaction Layer
- multilingual interface, structured report output, feedback loop, async batch operations.

### 4) Technical Consensus (current best-known)
- Runtime: Python + Streamlit.
- Data/Index: JSON/CSV pipelines + ChromaDB.
- Model orchestration: OpenAI/Anthropic/Vertex/Gemini connectors (with MedGemma target path).
- Control abstractions: Trinity bridge, Nexus router, AGID mapping, deterministic gates.
- Compliance model: HIPAA/GDPR/PIPL as architecture-level constraint (implementation depth varies by module).

### 5) Canonical Product Spec Recommendation (v1)
- Single canonical runtime entry for production requests.
- Canonical data contract:
  - input intent schema,
  - AGID/asset schema,
  - compliance context schema,
  - route output schema (clinical + operational + economic).
- Mandatory environment profiles:
  - local dev,
  - audit/staging,
  - production sovereign regions.
- Quality bars:
  - deterministic gate pass metrics,
  - route confidence metrics,
  - p95 latency per region,
  - compliance audit trace completeness.

## [Critical Gaps]
### A. Logic Voids (most urgent)
1. Compliance implementation depth gap
- Several docs define HIPAA/GDPR/PIPL architecture, but execution evidence shows parts still framework-level (consent/rule engine not fully closed-loop).

2. MedGemma deployment gap
- "Deterministic orchestration for Med-Gemini/MedGemma" is a repeated concept, but production-grade model integration and evaluation workflow remain partial.

3. Dual-path execution gap
- Narrative trends toward one sovereign path, while implementation notes still describe dual-entry/dual-routing behavior in places.

4. Data contract consistency gap
- Multiple "final" datasets and naming variants exist; canonical dataset lineage and authoritative production dataset are not yet fully singularized.

### B. Conflict Points (require human arbitration)
1. Product identity conflict
- "Global medical asset exchange/Nasdaq" vs "clinical decision support navigator".
- Arbitration needed: primary regulatory framing and market category.

2. Deterministic certainty wording conflict
- Docs use strong certainty language, while implementation includes fallbacks/stubs and variable data completeness.
- Arbitration needed: approved external claim language.

3. Coverage claim conflict
- "200k+ global nodes" appears in concept material; implementation snapshots show lower active mapped registry sizes.
- Arbitration needed: what counts as onboarded vs verifiably routable in production.

4. Commercial model conflict
- Shadow-billing/value model is central in strategy docs but not uniformly encoded as enforceable product contract across all execution paths.
- Arbitration needed: billing logic that is legally and operationally shippable.

### C. Documents that should be added immediately
1. `AMANI_PRODUCT_REQUIREMENTS_BASELINE.md`
- exact user segments, product boundary, non-goals, regulated usage statements.

2. `AMANI_CANONICAL_DATA_CONTRACT.md`
- authoritative schemas, lineage policy, "final dataset" governance, deprecation rules.

3. `AMANI_COMPLIANCE_IMPLEMENTATION_SPEC.md`
- consent model, region policy matrix, logging and retention controls, audit trace requirements.

4. `AMANI_MODEL_POLICY_AND_EVAL.md`
- model selection policy, fallback policy, benchmark sets, bias and robustness protocol.

5. `AMANI_RELEASE_GATES.md`
- minimum technical, security, compliance, and performance criteria for industrial delivery.

## Decision Note
This reconstruction prioritizes newer materials (late Jan to Feb execution summaries) over early-Jan conceptual text where contradictions appear.
