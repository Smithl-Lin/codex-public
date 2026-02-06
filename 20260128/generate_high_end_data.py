# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
A.M.A.N.I. 高端医疗主诉合成数据生成脚本
生成 10,000 条用于模型训练的结构化 JSON 数据，覆盖 BCI / 基因治疗 / 干细胞再生 / 高端临床研究。
Schema: request_id, original_inquiry, standard_mapping, asset_category, l1_entropy_target
"""
import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any, Iterable, Tuple

# ------------------------------------------------------------------------------
# 固定种子以保证可复现；规模与输出路径
# ------------------------------------------------------------------------------
RANDOM_SEED = 2026
TOTAL_RECORDS = 10_000
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CODEX_WORKSPACE = PROJECT_ROOT / "CODEX_WORKSPACE"
OUTPUT_FILE = str(CODEX_WORKSPACE / "amani_training_10k.json")
REQUEST_ID_PREFIX = "AM-REQ-2026-"
CATEGORIES = ["BCI", "Gene_Therapy", "Stem_Cell", "Clinical_Trial"]
MAX_WORKERS = 6
RATE_LIMIT_PER_SEC = 50  # soft limit for generation loop (tokens/sec equivalent)

# ------------------------------------------------------------------------------
# 1. BCI (脑机接口) — 语音假体、侵入式电极、Neuralink/BrainGate 等
# ------------------------------------------------------------------------------
BCI_PROJECTS = [
    "Neuralink", "BrainGate", "Speech Neuroprosthesis", "Synchron Stentrode",
    "Paradromics", "Wyss Center", "Blackrock Neurotech", "Precision Neuroscience",
]
BCI_TERMS = [
    "invasive cortical electrode", "speech prosthesis", "motor neuroprosthesis",
    "BCI for ALS", "locked-in syndrome", "intracortical array", "ECoG",
    "brain-computer interface", "neural decoding", "speech decoding",
    "脑机接口", "语音神经假体", "侵入式电极", "运动皮层解码",
]
BCI_INQUIRY_TEMPLATES = [
    "Patient with {} seeking evaluation for {}; interested in {} trials.",
    "Family member with ALS, exploring {} or {} for communication restoration.",
    "Neurologist referral: {} candidate for {}; request information on {} eligibility.",
    "海外求诊：患者{}，希望评估{}或{}项目参与资格。",
    "Urgent: {} diagnosis, seeking centers offering {} / {} clinical programs.",
    "Consultation request: {} for {}; interested in {} and similar neuroprosthesis options.",
    "研究者咨询：希望了解{}在{}适应症中的临床试验进展与入组标准。",
    "Patient with locked-in syndrome; family seeking {} or Speech Neuroprosthesis pathways.",
]


def _fill_template(tpl: str, args: List[str]) -> str:
    """Fill template placeholders {} with args; reuses last arg if needed."""
    out = tpl
    for i, a in enumerate(args):
        if "{}" not in out:
            break
        out = out.replace("{}", str(a), 1)
    while "{}" in out and args:
        out = out.replace("{}", str(args[-1]), 1)
    return out

BCI_STANDARD_MAPPINGS = [
    "Brain-computer interface (BCI) for motor/speech restoration",
    "Invasive neural interface; speech neuroprosthesis",
    "Cortical electrode array; motor neuroprosthesis",
    "BCI clinical trial; ALS or locked-in syndrome",
]

# ------------------------------------------------------------------------------
# 2. 基因治疗 — DMD, SMA, 镰状细胞, AAV, CRISPR
# ------------------------------------------------------------------------------
GENE_PROJECTS = [
    "ELEVIDYS", "Zolgensma", "Casgevy", "Lyfgenia", "SRP-9001",
    "AAV9", "CRISPR-Cas9", "gene replacement therapy", "exon skipping",
]
GENE_TERMS = [
    "Duchenne muscular dystrophy", "DMD", "SMA", "spinal muscular atrophy",
    "sickle cell disease", "beta-thalassemia", "AAV vector", "gene therapy",
    "镰状细胞贫血", "杜氏肌营养不良", "SMA基因治疗", "CRISPR疗法",
]
GENE_INQUIRY_TEMPLATES = [
    "Child with {}; family seeking {} (ELEVIDYS) or other approved gene therapy options.",
    "Patient with {}; requesting information on {} and {} access programs.",
    "海外求药：{}患者，希望了解{}、Casgevy或Zolgensma的用药与临床试验。",
    "Geneticist referral: {} confirmed; exploring {} and {} trials.",
    "Urgent consultation: {} diagnosis, seeking {} / {} availability and eligibility.",
    "Researcher inquiry: {} delivery and {} outcomes in {}; trial design interest.",
    "家长咨询：患儿确诊{}，寻求{}或Zolgensma相关中心及入组标准。",
    "Patient with sickle cell disease; interested in Casgevy or Lyfgenia and long-term follow-up.",
]

GENE_STANDARD_MAPPINGS = [
    "Gene therapy; AAV-based or CRISPR-based; DMD/SMA/sickle cell",
    "Gene replacement or gene editing; rare disease",
    "AAV vector gene therapy; neuromuscular or hemoglobinopathy",
    "CRISPR-Cas9 therapy; sickle cell or thalassemia",
]

# ------------------------------------------------------------------------------
# 3. 干细胞/再生医学 — iPSC, 帕金森, 心肌, 类器官
# ------------------------------------------------------------------------------
STEM_PROJECTS = [
    "iPSC", "induced pluripotent stem cell", "dopaminergic neuron", "cardiomyocyte",
    "organoid", "cell replacement", "Parkinson", "heart failure", "spinal cord injury",
]
STEM_TERMS = [
    "iPSC-derived neuron", "cell therapy", "regenerative medicine", "clinical trial",
    "帕金森", "心肌修复", "类器官移植", "干细胞分化", "多能干细胞",
]
STEM_INQUIRY_TEMPLATES = [
    "Patient with advanced {}; seeking {} or iPSC-derived neuron replacement trials.",
    "Cardiologist referral: {} with reduced EF; interested in {} or cardiac cell therapy.",
    "海外求诊：{}患者，希望评估{}或类器官相关临床研究入组。",
    "Family seeking {} therapy for {}; request centers with {} programs.",
    "Researcher inquiry: {} manufacturing and {} transplantation for {}; GMP requirements.",
    "Neurologist: {} patient, exploring {} and DBS; want frontier trial options.",
    "患者主诉：{}晚期，寻求iPSC/干细胞治疗方案及国际多中心试验信息。",
    "Consultation: {} with spinal cord injury; interested in {} or neural cell therapy.",
]

STEM_STANDARD_MAPPINGS = [
    "iPSC-derived cell therapy; Parkinson or cardiac or neural",
    "Stem cell / regenerative medicine; cell replacement",
    "Organoid or cell-based therapy; clinical trial",
    "Pluripotent stem cell; differentiated cell transplant",
]

# ------------------------------------------------------------------------------
# 4. 高端临床研究 — mRNA 疫苗、双抗、ADC、联合免疫
# ------------------------------------------------------------------------------
TRIAL_PROJECTS = [
    "mRNA cancer vaccine", "bispecific antibody", "ADC", "antibody-drug conjugate",
    "CAR-T", "immune checkpoint", "KRAS G12C", "personalized neoantigen",
]
TRIAL_TERMS = [
    "melanoma", "NSCLC", "solid tumor", "Phase II/III", "combination immunotherapy",
    "mRNA vaccine", "双特异性抗体", "ADC联合治疗", "个体化疫苗",
]
TRIAL_INQUIRY_TEMPLATES = [
    "Patient with {} ({}); seeking {} or {} clinical trials, preferably Phase II/III.",
    "Oncologist referral: {} positive; interested in {} inhibitors and {} combinations.",
    "海外求药：{}患者，希望参加{}或mRNA癌症疫苗相关试验。",
    "Consultation: {} with advanced {}; request {} and ADC immunotherapy options.",
    "Researcher inquiry: {} trial design and {} with checkpoint inhibition.",
    "患者家属咨询：{}晚期，寻求{}、双抗或ADC联合方案及入组条件。",
    "Urgent: {} mutation confirmed; seeking {} trials and bispecific antibody programs.",
    "Request for second opinion: {}; interest in personalized neoantigen vaccine and CAR-T.",
]

TRIAL_STANDARD_MAPPINGS = [
    "High-end clinical trial; mRNA vaccine / bispecific / ADC / immunotherapy",
    "Oncology clinical research; targeted or immune therapy",
    "Phase II/III trial; solid tumor or hematologic",
    "Combination immunotherapy; biomarker-driven",
]

# ------------------------------------------------------------------------------
# 语态修饰（增加多样性）
# ------------------------------------------------------------------------------
TONE_PREFIXES = [
    "", "Urgent: ", "Second opinion requested: ", "Family seeking information: ",
    "海外求诊：", "研究者咨询：", "Referral from specialist: ",
]
TONE_SUFFIXES = [
    "", " Would like to discuss eligibility and timeline.",
    " 希望了解入组标准与中心列表。", " Please advise on next steps.",
]

# ------------------------------------------------------------------------------
# 生成单条记录
# ------------------------------------------------------------------------------
def generate_one_bci(index: int, rng: random.Random) -> Dict[str, Any]:
    proj = rng.choice(BCI_PROJECTS)
    proj2 = rng.choice([p for p in BCI_PROJECTS if p != proj])
    term = rng.choice(BCI_TERMS)
    tpl = rng.choice(BCI_INQUIRY_TEMPLATES)
    inquiry = _fill_template(tpl, [term, proj, proj2])
    prefix = rng.choice(TONE_PREFIXES)
    suffix = rng.choice(TONE_SUFFIXES)
    original = (prefix + inquiry + suffix).strip()
    return {
        "request_id": REQUEST_ID_PREFIX + str(index).zfill(5),
        "original_inquiry": original,
        "standard_mapping": rng.choice(BCI_STANDARD_MAPPINGS),
        "asset_category": "BCI",
        "l1_entropy_target": round(rng.uniform(0.5, 0.9), 4),
    }


def generate_one_gene(index: int, rng: random.Random) -> Dict[str, Any]:
    term = rng.choice(GENE_TERMS)
    proj = rng.choice(GENE_PROJECTS)
    proj2 = rng.choice([p for p in GENE_PROJECTS if p != proj][:5])
    tpl = rng.choice(GENE_INQUIRY_TEMPLATES)
    inquiry = _fill_template(tpl, [term, proj, proj2])
    prefix = rng.choice(TONE_PREFIXES)
    suffix = rng.choice(TONE_SUFFIXES)
    original = (prefix + inquiry + suffix).strip()
    return {
        "request_id": REQUEST_ID_PREFIX + str(index).zfill(5),
        "original_inquiry": original,
        "standard_mapping": rng.choice(GENE_STANDARD_MAPPINGS),
        "asset_category": "Gene_Therapy",
        "l1_entropy_target": round(rng.uniform(0.5, 0.9), 4),
    }


def generate_one_stem(index: int, rng: random.Random) -> Dict[str, Any]:
    proj = rng.choice(STEM_PROJECTS)
    term = rng.choice(STEM_TERMS)
    proj2 = rng.choice([p for p in STEM_PROJECTS if p != proj][:5])
    tpl = rng.choice(STEM_INQUIRY_TEMPLATES)
    inquiry = _fill_template(tpl, [term, proj, proj2])
    prefix = rng.choice(TONE_PREFIXES)
    suffix = rng.choice(TONE_SUFFIXES)
    original = (prefix + inquiry + suffix).strip()
    return {
        "request_id": REQUEST_ID_PREFIX + str(index).zfill(5),
        "original_inquiry": original,
        "standard_mapping": rng.choice(STEM_STANDARD_MAPPINGS),
        "asset_category": "Stem_Cell",
        "l1_entropy_target": round(rng.uniform(0.5, 0.9), 4),
    }


def generate_one_trial(index: int, rng: random.Random) -> Dict[str, Any]:
    proj = rng.choice(TRIAL_PROJECTS)
    term = rng.choice(TRIAL_TERMS)
    proj2 = rng.choice([p for p in TRIAL_PROJECTS if p != proj][:5])
    tpl = rng.choice(TRIAL_INQUIRY_TEMPLATES)
    inquiry = _fill_template(tpl, [term, proj, proj2])
    prefix = rng.choice(TONE_PREFIXES)
    suffix = rng.choice(TONE_SUFFIXES)
    original = (prefix + inquiry + suffix).strip()
    return {
        "request_id": REQUEST_ID_PREFIX + str(index).zfill(5),
        "original_inquiry": original,
        "standard_mapping": rng.choice(TRIAL_STANDARD_MAPPINGS),
        "asset_category": "Clinical_Trial",
        "l1_entropy_target": round(rng.uniform(0.5, 0.9), 4),
    }


GENERATORS = {
    "BCI": generate_one_bci,
    "Gene_Therapy": generate_one_gene,
    "Stem_Cell": generate_one_stem,
    "Clinical_Trial": generate_one_trial,
}


class RateLimiter:
    """Thread-safe token-bucket rate limiter (soft QPS control)."""

    def __init__(self, rate_per_sec: float):
        self._rate = max(rate_per_sec, 1.0)
        self._capacity = self._rate
        self._tokens = self._rate
        self._lock = threading.Lock()
        self._last = time.perf_counter()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.perf_counter()
                elapsed = now - self._last
                self._last = now
                self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
            time.sleep(0.001)


def _build_tasks(total: int) -> List[Tuple[str, int]]:
    per_category = total // len(CATEGORIES)
    remainder = total % len(CATEGORIES)
    counts = [per_category + (1 if i < remainder else 0) for i in range(len(CATEGORIES))]
    tasks: List[Tuple[str, int]] = []
    global_index = 0
    for cat, count in zip(CATEGORIES, counts):
        for _ in range(count):
            tasks.append((cat, global_index))
            global_index += 1
    return tasks


def _worker(task: Tuple[str, int], seed_offset: int, limiter: RateLimiter) -> Dict[str, Any]:
    cat, index = task
    rng = random.Random(RANDOM_SEED + seed_offset + index)
    limiter.acquire()
    return GENERATORS[cat](index, rng)


# ------------------------------------------------------------------------------
# 主流程：均匀分布生成 10,000 条
# ------------------------------------------------------------------------------
def generate_dataset(total: int = TOTAL_RECORDS, output_path: str = OUTPUT_FILE) -> List[Dict[str, Any]]:
    """
    生成 total 条记录，四类资产均匀分布（每类 total//4，余数按序分配）。
    写入 output_path 的 JSON 文件（UTF-8）。
    """
    tasks = _build_tasks(total)
    limiter = RateLimiter(RATE_LIMIT_PER_SEC)
    records: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(_worker, task, 1000, limiter) for task in tasks]
        for f in as_completed(futures):
            records.append(f.result())
    # request_id 必须唯一且连续；按 request_id 排序后重写 index
    records.sort(key=lambda r: r["request_id"])
    for i, rec in enumerate(records):
        rec["request_id"] = REQUEST_ID_PREFIX + str(i).zfill(5)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return records


def main():
    print(f"Generating {TOTAL_RECORDS} records (seed={RANDOM_SEED})...")
    records = generate_dataset(TOTAL_RECORDS, OUTPUT_FILE)
    counts = {}
    for r in records:
        c = r["asset_category"]
        counts[c] = counts.get(c, 0) + 1
    print(f"Written to {OUTPUT_FILE}")
    print("Distribution:", counts)
    print("Sample request_id range:", records[0]["request_id"], "-", records[-1]["request_id"])
    print("Sample record:", json.dumps(records[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
