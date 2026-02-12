# TECHNICAL CLAIMS DOCUMENT
## A.M.A.N.I. Platform (Advanced Medical Asset Navigation Intelligence)
## USPTO Provisional Patent Application

**Document Version:** 1.0
**Date:** February 8, 2026
**Applicant:** [To be specified]
**Filing Type:** Provisional Patent Application
**Technical Field:** Medical Resource Allocation Systems, Clinical Decision Support, Healthcare Information Technology

---

## ABSTRACT

The present invention relates to a hierarchical medical asset allocation system comprising a multi-layered architecture for precision-gated medical resource matching. The system employs Shannon entropy-based precision gating with a D ≤ 0.79 threshold, hard anchor boolean interception for atomic technical term prioritization, dual-phase semantic retrieval with N=100 pool re-ranking, and cultural equalization pre-processing to achieve compliance-aware, multi-regional medical asset allocation with dynamic billing activation based on precision-distance metrics.

---

## BACKGROUND OF THE INVENTION

Current medical resource allocation systems suffer from several technical deficiencies: (1) lack of precision-based quality gates leading to low-confidence matches, (2) inability to preserve atomic-level technical specifications during semantic search, resulting in "downgrade matching," (3) cultural and linguistic biases in patient intake processing, and (4) inadequate real-time resource availability tracking across multi-regional healthcare networks.

The present invention addresses these deficiencies through a novel five-layer architecture combining entropy-based precision gates, hard anchor boolean interception, dual-phase retrieval with semantic re-ranking, and a Centurion four-component resource monitoring system.

---

## DETAILED DESCRIPTION OF THE INVENTION

### System Architecture Overview

The AMANI platform implements a five-layer hierarchical architecture:

- **Layer 1 (L1):** Sentinel - Entropy-based precision gating
- **Layer 2 (L2):** Asset Layer - Four-component Centurion architecture
- **Layer 2.5 (L2.5):** Value Orchestration - Commercial logic and lifecycle planning
- **Layer 3 (L3):** Global Nexus - Intent-to-AGID mapping with Graph Neural Network
- **Layer 4 (L4):** Interface Layer - Multi-modal presentation and feedback optimization

---

## CLAIMS

### INDEPENDENT CLAIMS

**CLAIM 1.** A medical asset allocation system comprising:

(a) an entropy-based sentinel gate configured to:
    (i) calculate Shannon entropy over a sliding window of input text tokens,
    (ii) compute a precision-distance metric D as a function of mean entropy,
    (iii) compute entropy variance across the input text,
    (iv) reject inputs where D exceeds a predetermined threshold of 0.79 or entropy variance exceeds 0.005, and
    (v) generate a strategic intercept identifier (AGID) for rejected inputs;

(b) a cultural equalization preprocessor configured to:
    (i) detect locale from input text using character set pattern matching,
    (ii) apply phrase mapping from a multilingual phrase database to canonical medical terminology,
    (iii) append canonical phrase context to equalized text, and
    (iv) output culturally-neutral text for downstream processing;

(c) a hard anchor boolean interceptor configured to:
    (i) identify atomic technical terms in equalized input text through case-insensitive substring matching,
    (ii) maintain a configurable set of atomic technical terms including at least: iPS, BCI, DBS, KRAS G12C, CAR-T, ADC, Neural Interface, and mRNA Vaccine,
    (iii) extract a hard anchor set from identified terms, and
    (iv) use the hard anchor set for secondary re-ranking of retrieval results;

(d) a dual-phase semantic retrieval engine configured to:
    (i) retrieve a pool of N candidate assets from a vector database, where N is at least 100,
    (ii) compute semantic similarity scores for each candidate,
    (iii) re-rank candidates by prioritizing those containing at least one hard anchor term when hard anchors are present,
    (iv) sort candidates within priority groups by semantic score, and
    (v) return top-k candidates after re-ranking, where k is less than N;

(e) a Centurion four-component asset monitor comprising:
    (i) a Global Patient Resources component tracking patient-centric data across multiple geographic regions,
    (ii) an Advanced Therapeutic Assets component indexing high-end medical treatments including FDA clinical trials, cell therapy, gene therapy, stem cell research, and brain-computer interface projects,
    (iii) a Principal Investigator Registry component mapping principal investigators to therapeutic projects, and
    (iv) a Lifecycle Pulse Monitor component executing background scans at predetermined intervals to detect additions, deletions, and status changes across components (i)-(iii);

(f) a precision-gated access controller configured to:
    (i) receive a precision-distance value D,
    (ii) permit access to Centurion components (i)-(iv) only when D is less than or equal to 0.79, and
    (iii) return null when D exceeds 0.79;

(g) a Graph Neural Network asset anchor configured to:
    (i) convert intent summary text to a feature vector,
    (ii) query a persistent vector database using the feature vector,
    (iii) retrieve asset candidates with similarity scores,
    (iv) apply hard anchor re-ranking when hard anchors are present,
    (v) generate Asset Global Identifiers (AGIDs) for matched assets, and
    (vi) return a list of AGIDs with associated scores;

(h) a commercial value orchestrator configured to:
    (i) process entity-specific commercial logic for Insurance, Family Office, and Pharma entities,
    (ii) generate full lifecycle strategy chains comprising Treatment, Recovery, and Psychology stages,
    (iii) calculate billing matrices only when precision-distance D is less than or equal to 0.79,
    (iv) apply subscription-tier pricing or per-match pricing based on configuration, and
    (v) output shadow quotes with AGID-tagged line items; and

(i) a multi-modal interface presenter configured to:
    (i) receive shadow quotes from the commercial value orchestrator,
    (ii) render shadow quotes in at least four presentation modes: TEXT, STRUCTURED, HTML, and MARKDOWN,
    (iii) present strategy stages from the lifecycle chain, and
    (iv) collect user feedback for asset weight optimization.

**CLAIM 2.** A computer-implemented method for precision-gated medical asset allocation comprising:

(a) receiving input text representing a patient medical inquiry;

(b) computing Shannon entropy and entropy variance for the input text using a sliding window approach;

(c) calculating a precision-distance metric D as a function of the Shannon entropy;

(d) comparing D to a hard threshold of 0.79 and the entropy variance to a threshold of 0.005;

(e) when D exceeds 0.79 or entropy variance exceeds 0.005:
    (i) generating a strategic intercept AGID,
    (ii) terminating further processing, and
    (iii) returning the intercept AGID;

(f) when D is less than or equal to 0.79 and entropy variance is less than or equal to 0.005:
    (i) applying cultural equalization preprocessing to generate equalized text,
    (ii) extracting hard anchor terms from the equalized text using atomic technical term matching,
    (iii) retrieving N candidate assets from a vector database where N is at least 100,
    (iv) re-ranking the N candidates by prioritizing those containing at least one hard anchor term,
    (v) selecting top-k candidates from the re-ranked list where k is less than N,
    (vi) accessing Centurion four-component asset data,
    (vii) generating shadow quotes with precision-gated billing activation, and
    (viii) presenting results in multiple presentation modes.

**CLAIM 3.** A data structure stored in non-transitory computer-readable memory for medical asset identification comprising:

(a) an Asset Global Identifier (AGID) field comprising:
    (i) a namespace identifier,
    (ii) a node type identifier,
    (iii) a cryptographic hash of a composite key comprising the namespace, node type, and raw identifier,
    wherein the hash is truncated to 12 hexadecimal characters;

(b) a precision-distance metadata field storing a D value representing precision quality;

(c) an asset category field storing one of: Gold Standard, Frontier, or Recovery;

(d) a lifecycle stage field storing one of: Treatment, Recovery, or Psychology;

(e) a hard anchor match field indicating whether the asset contains atomic technical terms;

(f) a regional compliance field storing at least one of: NA, EU, Asia-Pacific, Commonwealth;

(g) a billing activation flag set to TRUE only when associated D value is less than or equal to 0.79; and

(h) a semantic embedding vector of predetermined dimensionality for similarity computation.

### DEPENDENT CLAIMS

**CLAIM 4.** The system of claim 1, wherein the Shannon entropy calculation uses a window size of 5 tokens and computes per-position entropy as:

E_i = -Σ(p_j × log_2(p_j))

where p_j is the frequency of token j within the window centered at position i, and the mean entropy and variance are calculated across all positions.

**CLAIM 5.** The system of claim 1, wherein the precision-distance metric D is computed as:

D = min(1.0, 1.2 - mean_entropy × 0.3)

and D is required to be less than or equal to 0.79 for processing to continue beyond Layer 1.

**CLAIM 6.** The system of claim 1, wherein the cultural equalization preprocessor maintains a phrase mapping database comprising:

(a) source phrases in multiple languages including at least Chinese, Japanese, Korean, German, French, and Spanish;

(b) canonical medical complaint phrases in English; and

(c) category tags selected from: meta, symptom, condition, intent, treatment.

**CLAIM 7.** The system of claim 6, wherein the cultural equalization preprocessor applies substring matching with case sensitivity preserved for non-ASCII scripts and case-insensitive matching for ASCII scripts.

**CLAIM 8.** The system of claim 1, wherein the hard anchor boolean interceptor atomic technical terms comprise at least:

(a) stem cell and regenerative medicine terms: iPS, stem cell, 干细胞, Dopaminergic;

(b) neural interface terms: BCI, DBS, Neural Interface, Neuralink, brain-computer interface, 脑机接口, Subthalamic;

(c) oncology precision medicine terms: KRAS G12C, G12C, CAR-T, ADC, mRNA Vaccine.

**CLAIM 9.** The system of claim 1, wherein the dual-phase semantic retrieval engine:

(a) retrieves N=100 candidates in a first phase using semantic similarity;

(b) partitions candidates into two groups in a second phase:
    (i) candidates containing at least one hard anchor term, and
    (ii) candidates containing no hard anchor terms;

(c) sorts each group independently by semantic score in descending order;

(d) concatenates the groups with hard anchor candidates first; and

(e) selects top-k candidates from the concatenated list, where k is typically 5.

**CLAIM 10.** The system of claim 1, wherein the Centurion Global Patient Resources component:

(a) ingests patient-centric data from JSON data sources;

(b) infers geographic region using keyword matching for region-specific terms;

(c) assigns AGIDs with namespace "GPR" and node type "PATIENT";

(d) indexes records by raw identifier with region, category, title, status, and timestamp metadata; and

(e) generates region count summaries on snapshot requests.

**CLAIM 11.** The system of claim 1, wherein the Centurion Advanced Therapeutic Assets component:

(a) filters assets using tag matching for at least: fda, clinical trial, cell therapy, gene therapy, stem cell, bci, brain-computer, neuro;

(b) assigns AGIDs with namespace "ATA" and node type "ASSET";

(c) indexes assets by source file and raw identifier; and

(d) tracks asset status including at least: ACTIVE, RECRUITING, COMPLETED, TERMINATED.

**CLAIM 12.** The system of claim 1, wherein the Centurion Principal Investigator Registry:

(a) assigns AGIDs with namespace "PI" and node type "REGISTRY";

(b) maintains bidirectional linkage between principal investigators and therapeutic projects;

(c) accepts optional therapeutic asset ID lists for linkage synchronization; and

(d) returns project-to-PI mapping in snapshot output.

**CLAIM 13.** The system of claim 1, wherein the Centurion Lifecycle Pulse Monitor:

(a) executes background scans at 12-hour intervals by default;

(b) computes difference sets between current and previous snapshots;

(c) records events of type ADDITION, DELETION, or STATUS_CHANGE;

(d) maintains a changelog with timestamp, event type, component identifier, asset identifier, and AGID;

(e) persists changelog to JSON file storage;

(f) limits changelog to most recent 5000 entries; and

(g) provides lifecycle summary with counts of additions, deletions, and status changes.

**CLAIM 14.** The system of claim 1, wherein the precision-gated access controller:

(a) receives D precision values from Layer 1 sentinel;

(b) compares D to a hard threshold of 0.79;

(c) invokes Centurion component snapshot methods only when D ≤ 0.79;

(d) passes snapshot through Layer 2.5 value orchestrator;

(e) enriches snapshot with shadow quote and lifecycle journey plan; and

(f) dispatches enriched snapshot to Layer 3 global nexus.

**CLAIM 15.** The system of claim 1, wherein the Graph Neural Network asset anchor:

(a) uses a persistent ChromaDB vector database;

(b) caches collection count on initialization to reduce query overhead during batch processing;

(c) converts intent summary text to query vector using hash-based feature extraction when neural embeddings are unavailable;

(d) queries the vector database with configurable n_results parameter;

(e) receives distances and converts to scores using formula: score = max(0.0, 1.0 - distance); and

(f) returns AGID-score pairs sorted by score in descending order.

**CLAIM 16.** The system of claim 15, wherein hard anchor re-ranking:

(a) requests documents and metadatas in addition to distances when hard anchors are present;

(b) concatenates document text and metadata for each candidate;

(c) performs case-insensitive substring matching for each hard anchor term;

(d) classifies each candidate as "with_anchor" or "without_anchor";

(e) sorts each classification group by score independently; and

(f) returns concatenated list with "with_anchor" group first.

**CLAIM 17.** The system of claim 1, wherein the commercial value orchestrator:

(a) implements entity-specific handlers for Insurance, Family_Office, and Pharma;

(b) for Insurance entities:
    (i) validates pre-authorization eligibility,
    (ii) determines coverage tier, and
    (iii) establishes claims linkage;

(c) for Family_Office entities:
    (i) assigns concierge service level,
    (ii) enables multi-jurisdiction support, and
    (iii) enforces discretion protocols;

(d) for Pharma entities:
    (i) establishes clinical trial linkage,
    (ii) aligns with R&D objectives, and
    (iii) performs compliance checking.

**CLAIM 18.** The system of claim 1, wherein the commercial value orchestrator lifecycle strategy:

(a) generates a chain of three stages: Treatment, Recovery, Psychology;

(b) assigns sequential AGID to each stage with namespace "VALUE" and node type "LIFECYCLE";

(c) maintains parent_id linkage to initial asset;

(d) propagates metadata from initial asset to all stages; and

(e) returns ordered list of stage objects with stage name, sequence number, AGID, and parent identifier.

**CLAIM 19.** The system of claim 1, wherein the billing matrix calculation:

(a) receives precision-distance D, AGID list, subscription tier, and optional per-match rates;

(b) returns null immediately when D > 0.79;

(c) when D ≤ 0.79:
    (i) retrieves subscription fee from tier table for tiers TRINITY_FULL ($299), DEGRADED_DUAL ($149), or STRATEGIC_VETO ($0),
    (ii) calculates per-match fees using provided rates or default base rate of $500,
    (iii) in TO_B_STRICT mode, applies per-match fee only to first asset,
    (iv) sums subscription fee, per-match total, and APH reserve buffer,
    (v) generates quote AGID with namespace "BILL" and node type "QUOTE",
    (vi) returns structured quote with status, D value, breakdown, and currency.

**CLAIM 20.** The system of claim 1, wherein the multi-modal interface presenter:

(a) receives shadow quote structure from Layer 2.5;

(b) implements TEXT mode rendering as plain text with line-by-line formatting;

(c) implements STRUCTURED mode rendering as nested dictionary with typed fields;

(d) implements HTML mode rendering with CSS styling and responsive layout;

(e) implements MARKDOWN mode rendering with headers, lists, and code blocks;

(f) includes AGID display in all modes; and

(g) displays billing activation status based on D ≤ 0.79 condition.

**CLAIM 21.** The method of claim 2, further comprising:

(a) loading configuration from JSON file containing:
    (i) precision_lock_threshold value of 0.79,
    (ii) variance_limit_numeric value of 0.005,
    (iii) atomic_technical_terms list,
    (iv) retrieval_pool_size_n value of 100,
    (v) downgrade_firewall boolean flag;

(b) applying configuration values to sentinel gate, hard anchor interceptor, and dual-phase retrieval engine.

**CLAIM 22.** The method of claim 2, further comprising:

(a) maintaining a protocol audit log;

(b) recording timestamp, intercept status, D value, entropy variance, and L3 origin for each request;

(c) appending log entries to persistent storage; and

(d) using log data for sovereignty compliance auditing.

**CLAIM 23.** The method of claim 2, further comprising:

(a) implementing concurrency guard with semaphore-based limiting;

(b) configuring maximum concurrent bridge calls to 8 by default;

(c) setting timeout for semaphore acquisition to 30 seconds;

(d) returning concurrency timeout error when semaphore cannot be acquired; and

(e) releasing semaphore after request completion or failure.

**CLAIM 24.** The method of claim 2, wherein the cultural equalization preprocessing:

(a) loads cultural complaint mapping from JSON file;

(b) detects locale using character set pattern matching for at least: Chinese (zh), Japanese (ja), Korean (ko), Arabic (ar);

(c) iterates through phrase mappings;

(d) for each mapping:
    (i) attempts regex match for all source phrases,
    (ii) performs case-insensitive match for ASCII phrases,
    (iii) performs exact match for non-ASCII phrases,
    (iv) replaces first occurrence with canonical phrase,
    (v) adds canonical phrase to additions list;

(e) appends canonical additions as bracketed suffix to equalized text.

**CLAIM 25.** The method of claim 2, wherein accessing Centurion four-component asset data comprises:

(a) invoking ingest methods for components 1, 2, and 3;

(b) executing Lifecycle Pulse Monitor run_cycle to ensure current data;

(c) retrieving snapshots from all four components;

(d) building unified current state keyed by (component, id);

(e) comparing with previous index to identify changes;

(f) generating changelog entries for additions, deletions, and status changes; and

(g) returning snapshot with component summaries and lifecycle change summary.

**CLAIM 26.** The data structure of claim 3, wherein the AGID generation algorithm:

(a) concatenates namespace, node type, and raw identifier with colon separators;

(b) applies SHA-256 cryptographic hash to concatenated string;

(c) encodes hash output as hexadecimal;

(d) truncates hexadecimal string to first 12 characters;

(e) converts truncated string to uppercase; and

(f) prepends "AGID-" followed by namespace and node type with hyphen separators.

**CLAIM 27.** The data structure of claim 3, further comprising:

(a) a compliance_region field storing allowed regions as list;

(b) a consent_verified boolean field;

(c) a data_minimization_applied boolean field;

(d) a audit_trail_id linking to external audit log; and

(e) a retention_policy field specifying data retention duration.

**CLAIM 28.** The system of claim 1, further comprising:

(a) a medical reasoner module configured to:
    (i) receive equalized input text and Layer 1 context,
    (ii) generate strategy with stages in categories Gold Standard, Frontier, Recovery,
    (iii) produce intent summary from input text,
    (iv) generate resource_matching_suggestion specifying imaging, therapeutics, and pi_experts;

(b) an orchestrator configured to:
    (i) audit medical reasoner output,
    (ii) compute reasoning cost from strategy complexity,
    (iii) compute compliance score from resource suggestions and category assignments,
    (iv) apply path truncation when entropy variance exceeds limit,
    (v) apply forced desensitization when compliance score falls below minimum.

**CLAIM 29.** The system of claim 1, further comprising:

(a) a Global Nexus dispatcher configured to:
    (i) accept enriched snapshot from Layer 2.5,
    (ii) extract component totals from Layer 2 snapshot,
    (iii) extract shadow quote from Layer 2.5,
    (iv) extract multi-point journey plan from Layer 2.5,
    (v) generate timestamp,
    (vi) assemble nexus result with layer identifier, D precision, component summaries, shadow quote, journey plan, nexus status, and audit readiness flag.

**CLAIM 30.** The system of claim 1, further comprising:

(a) a feedback optimizer configured to:
    (i) collect user feedback including rating and comment,
    (ii) extract AGIDs from associated query,
    (iii) compute weight adjustment delta based on rating,
    (iv) apply delta to asset weights in persistent storage,
    (v) log feedback event with timestamp and AGID associations,
    (vi) aggregate feedback over time window for trend analysis,
    (vii) trigger asset re-ranking when cumulative adjustments exceed threshold.

---

## TECHNICAL ADVANTAGES

The present invention provides several technical advantages over prior art medical asset allocation systems:

1. **Precision Quality Gate:** The Shannon entropy-based D ≤ 0.79 threshold prevents low-confidence matches from consuming downstream computational resources and presenting unreliable results to users.

2. **Atomic Technical Term Preservation:** The hard anchor boolean interception mechanism ensures that critical medical terminology such as "KRAS G12C", "iPS", and "BCI" are not lost during semantic search, preventing inappropriate downgrade matching to generic alternatives.

3. **Cultural Equalization:** The preprocessing layer normalizes multilingual and culturally-diverse patient descriptions to canonical medical terminology before semantic processing, reducing bias and improving match quality across diverse populations.

4. **Dual-Phase Retrieval:** The N=100 pool retrieval followed by hard anchor re-ranking provides a technical solution to the semantic search problem where relevant but highly specific matches would be excluded by small top-k selection.

5. **Real-Time Asset Tracking:** The Centurion Lifecycle Pulse Monitor background scanning architecture provides up-to-date resource availability without requiring synchronous API calls during patient matching workflows.

6. **Precision-Distance Billing Activation:** Coupling billing system activation to the D ≤ 0.79 threshold ensures that charges only occur for high-confidence matches, reducing disputes and improving system trust.

7. **AGID Sovereign Protocol:** The cryptographic hash-based AGID structure provides globally unique identifiers with namespace isolation and tamper evidence, enabling secure multi-institutional asset tracking and audit trails.

8. **Five-Layer Architecture:** The hierarchical L1-L4 design with sovereign protocol enforcement at each layer provides defense-in-depth against low-quality matches, ensures regulatory compliance, and enables independent testing and validation of each layer.

---

## CLAIMS SUMMARY

| Claim # | Type | Focus Area |
|---------|------|------------|
| 1 | Independent | System architecture with 9 major components |
| 2 | Independent | Method for precision-gated allocation |
| 3 | Independent | AGID data structure |
| 4-5 | Dependent | Shannon entropy calculation specifics |
| 6-7 | Dependent | Cultural equalization details |
| 8-9 | Dependent | Hard anchor boolean interception |
| 10-13 | Dependent | Centurion four components |
| 14 | Dependent | Precision-gated access control |
| 15-16 | Dependent | GNN asset anchor with re-ranking |
| 17-20 | Dependent | Commercial value orchestration |
| 21-25 | Dependent | Method implementation details |
| 26-27 | Dependent | AGID data structure details |
| 28 | Dependent | Medical reasoner integration |
| 29 | Dependent | Global Nexus dispatcher |
| 30 | Dependent | Feedback optimization |

**Total Claims: 30 (3 Independent, 27 Dependent)**

---

## TECHNICAL SPECIFICATIONS

### System Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| D threshold | 0.79 | Empirically determined precision-distance limit; values above 0.79 indicate insufficient semantic match quality |
| Variance limit | 0.005 | Shannon entropy variance threshold; higher values indicate input text ambiguity or noise |
| Retrieval pool N | 100 | Minimum pool size to ensure adequate hard anchor match candidates before re-ranking |
| Top-k selection | 5 (typical) | Final match count after re-ranking; configurable based on use case |
| Window size | 5 tokens | Sliding window for per-position entropy calculation |
| AGID hash length | 12 hex chars | Balances collision resistance with identifier compactness |
| Pulse scan interval | 12 hours | Centurion background scan frequency; balances freshness with system load |
| Max changelog | 5000 entries | Lifecycle event history retention limit |
| Concurrency limit | 8 calls | Default maximum concurrent bridge invocations |
| Semaphore timeout | 30 seconds | Maximum wait time for concurrency slot |

### Atomic Technical Terms (Representative Subset)

**Stem Cell & Regenerative:**
- iPS, induced pluripotent stem cells, 干细胞, Dopaminergic, stem cell

**Neural Interface:**
- BCI, DBS, Neural Interface, Neuralink, brain-computer interface, 脑机接口, Subthalamic

**Oncology Precision:**
- KRAS G12C, G12C, CAR-T, ADC (antibody-drug conjugate), mRNA Vaccine

### Asset Categories

1. **Gold Standard:** Evidence-based, FDA-approved, guideline-recommended treatments
2. **Frontier:** Experimental, clinical trial phase, cutting-edge therapeutics
3. **Recovery:** Post-acute care, rehabilitation, psychological support

### Lifecycle Stages

1. **Treatment:** Active intervention phase
2. **Recovery:** Post-treatment rehabilitation
3. **Psychology:** Mental health and cognitive support

### Regional Designations

- **NA:** North America
- **EU:** European Union
- **Asia-Pacific:** East Asia, Southeast Asia, Oceania
- **Commonwealth:** UK, Canada, Australia, India

---

## IMPLEMENTATION NOTES

### Software Architecture

The AMANI platform is implemented as a modular Python-based system with the following key modules:

1. **amani_trinity_bridge.py:** Core orchestration, ECNNSentinel, StaircaseMappingLLM, GNNAssetAnchor, TrinityBridge
2. **amani_cultural_equalizer_l2.py:** Cultural preprocessing and phrase mapping
3. **amah_centurion_injection.py:** Four-component asset monitoring system
4. **amani_value_layer_v4.py:** Commercial logic and billing matrix calculation
5. **amani_global_nexus_v4.py:** Global dispatch and nexus orchestration
6. **amani_interface_layer_v4.py:** Multi-modal presentation layer
7. **ontology_engine.py:** Medical ontology and query enhancement
8. **medical_reasoner.py:** Clinical reasoning and strategy generation
9. **billing_engine.py:** Precision-gated billing activation

### Data Persistence

- **ChromaDB:** Vector database for semantic asset retrieval (expert_map_global collection)
- **JSON Files:** Configuration (amah_config.json), asset sources (merged_data.json, all_trials.json, expert_map_data.json)
- **Audit Logs:** Sovereignty audit log (sovereignty_audit.log), Centurion changelog (centurion_pulse_changelog.json)

### External Integrations

- **ClinicalTrials.gov API:** Clinical trial data ingestion
- **FDA Device API:** Medical device registry
- **WHO TrialSearch:** International trial aggregation
- **NCI API:** National Cancer Institute trial data
- **MedGemma Endpoint:** Optional medical reasoning model endpoint

---

## NOVELTY AND NON-OBVIOUSNESS

### Novel Aspects

1. **Shannon Entropy Precision Gating:** While entropy has been used in NLP for text classification, its application as a hard precision gate (D ≤ 0.79) for medical resource allocation is novel. The specific formula D = min(1.0, 1.2 - mean_entropy × 0.3) with dual variance checking is not found in prior art.

2. **Hard Anchor Boolean Interception with Dual-Phase Retrieval:** The combination of large pool retrieval (N=100) followed by atomic term re-ranking addresses a specific technical problem in semantic search where highly relevant but terminology-specific results are excluded by small top-k selection. This two-phase approach with explicit hard anchor preservation is not taught in existing semantic search systems.

3. **Cultural Equalization as Preprocessing Layer:** While machine translation exists, the specific approach of canonical phrase mapping with locale detection and culturally-neutral medical terminology output, positioned as a mandatory preprocessing step before entropy gating, represents a novel system architecture element.

4. **Precision-Distance-Gated Billing Activation:** Coupling financial transaction activation to Shannon entropy-derived precision metrics (D ≤ 0.79) creates a technical solution to the business problem of charging for low-quality matches. This tight coupling between quality metrics and billing systems is not taught in prior art.

5. **Centurion Four-Component Architecture with Lifecycle Pulse:** The specific four-component design (Global_Patient_Resources, Advanced_Therapeutic_Assets, PI_Registry, Lifecycle_Pulse_Monitor) with 12-hour background scanning and ADDITION/DELETION/STATUS_CHANGE event tracking represents a novel architecture for medical asset monitoring.

6. **AGID Sovereign Protocol:** While UUID systems exist, the specific AGID structure with namespace-type-hash composition, truncated SHA-256 (12 hex chars), and sovereign protocol enforcement at each layer represents a novel identifier system optimized for medical asset tracking.

### Non-Obvious Combinations

1. The combination of Shannon entropy (information theory) with medical semantic search (NLP) and financial billing activation (business logic) in a single unified system is non-obvious.

2. The specific threshold values (D ≤ 0.79, variance ≤ 0.005, N=100) are empirically optimized and not derivable from first principles.

3. The layered architecture with sovereign protocol enforcement at each layer, where each layer can independently reject requests, represents a non-obvious application of defense-in-depth principles to medical AI systems.

---

## POTENTIAL CONTINUATION CLAIMS

Future patent applications may claim:

1. **Machine Learning Optimization:** Methods for training the D threshold and atomic technical term list using reinforcement learning from user feedback.

2. **Multi-Modal Medical Reasoning:** Integration of medical imaging analysis with the text-based entropy gating system.

3. **Federated Asset Networks:** Cross-institutional AGID resolution protocols with privacy-preserving asset discovery.

4. **Regulatory Compliance Automation:** Automated generation of HIPAA, GDPR, and regional compliance documentation from Layer 3 dispatches.

5. **Real-Time Billing Negotiation:** Dynamic pricing based on D precision scores and asset availability.

---

## CONCLUSION

The AMANI platform represents a significant advancement in medical asset allocation systems through its novel combination of Shannon entropy-based precision gating, hard anchor boolean interception, cultural equalization preprocessing, dual-phase semantic retrieval, and Centurion four-component architecture. The technical claims presented herein protect the core algorithmic innovations, system architecture, and data structures that enable precision-gated, compliance-aware, multi-regional medical resource matching with dynamic billing activation.

---

**END OF TECHNICAL CLAIMS DOCUMENT**

---

## APPENDIX A: KEY FORMULAS

### Shannon Entropy (Per-Position)
```
E_i = -Σ(p_j × log_2(p_j))
where p_j = count(token_j in window_i) / window_size
```

### Precision-Distance Metric
```
D = min(1.0, 1.2 - mean_entropy × 0.3)
```

### Entropy Variance
```
variance = Σ((E_i - mean_entropy)²) / n
where n = number of positions
```

### Semantic Score from Distance
```
score = max(0.0, 1.0 - distance)
```

### AGID Generation
```
raw = "{namespace}:{node_type}:{raw_id}"
hash = SHA256(raw)
truncated = hash[0:12].upper()
AGID = f"AGID-{namespace}-{node_type}-{truncated}"
```

---

## APPENDIX B: SYSTEM CONFIGURATION SCHEMA

```json
{
  "alignment_logic": {
    "precision_lock_threshold": 0.79,
    "manual_audit_threshold": 1.35
  },
  "trinity_audit_gate": {
    "variance_tolerance": "DYNAMIC",
    "variance_limit_numeric": 0.005
  },
  "hard_anchor_boolean_interception": {
    "atomic_technical_terms": ["iPS", "BCI", "DBS", "KRAS G12C", "CAR-T", ...],
    "retrieval_pool_size_n": 100,
    "downgrade_firewall": true
  },
  "centurion_injection": {
    "enabled": true,
    "timeout_seconds": 5
  },
  "protocol_audit": {
    "enabled": true,
    "log_path": "sovereignty_audit.log"
  },
  "concurrency_guard": {
    "max_concurrent_bridge_calls": 8,
    "timeout_seconds": 30,
    "enabled": true
  }
}
```

---

**Document prepared by:** Claude Sonnet 4.5
**Technical analysis source:** AMANI Project codebase at C:\2025-12-01 Mayo-working\2026-01-22 Business projects\AMANI Project
**Filing recommendation:** Provisional patent application with 12-month continuation window for additional claims and international PCT filing.
