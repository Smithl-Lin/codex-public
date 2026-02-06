# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
# AMAH Weight Orchestrator V4.0 — 波形熵注入、variance>0.005 联动、AGID 输出

import math
import random
import json
import hashlib
import numpy as np

# ------------------------------------------------------------------------------
# AGID 体系
# ------------------------------------------------------------------------------
def to_agid(namespace: str, node_type: str, raw_id) -> str:
    sid = hashlib.sha256(f"{namespace}:{node_type}:{raw_id}".encode()).hexdigest()[:12].upper()
    return f"AGID-{namespace}-{node_type}-{sid}"


def calculate_sliding_entropy(text, window_size=5):
    """V4.0 注入：波形熵检测（轻量实现，无 PyTorch 依赖）。"""
    tokens = list(text)
    seq_len = len(tokens)
    entropy_seq = []
    for i in range(seq_len):
        start = max(0, i - window_size // 2)
        end = min(seq_len, i + window_size // 2 + 1)
        window = tokens[start:end]
        counts = {}
        for t in window:
            counts[t] = counts.get(t, 0) + 1
        ent = 0.0
        total = len(window)
        for c in counts.values():
            p = c / total
            ent -= p * math.log2(p) if p > 0 else 0
        entropy_seq.append(ent)
    variance = float(np.var(entropy_seq)) if entropy_seq else 0.0
    return entropy_seq, variance


VARIANCE_INTERCEPT_THRESHOLD = 0.005


class AMAHWeightOrchestrator:
    def __init__(self):
        self.DOMAIN_MATRIX = {
            "Parkinson": {
                "weights": {"vol": 0.35, "pi": 0.25, "aca": 0.15, "inst": 0.15, "rep": 0.10},
                "sigma": 1.25,
                "min_threshold": 0.79
            },
            "Longevity": {
                "weights": {"aca": 0.40, "inst": 0.25, "rep": 0.20, "pi": 0.10, "vol": 0.05},
                "sigma": 0.85,
                "min_threshold": 0.82
            },
            "Oncology": {
                "weights": {"pi": 0.30, "inst": 0.25, "aca": 0.20, "vol": 0.15, "rep": 0.10},
                "sigma": 1.40,
                "min_threshold": 0.80
            }
        }

    def detect_strategic_domain(self, query):
        q = query.lower()
        if any(k in q for k in ["dbs", "parkinson", "tremor", "stn", "movement"]):
            return "Parkinson"
        elif any(k in q for k in ["aging", "longevity", "nad+", "biomarker", "cell"]):
            return "Longevity"
        elif any(k in q for k in ["cancer", "oncology", "adc", "tumor", "trial"]):
            return "Oncology"
        return "Parkinson"

    def calculate_nonlinear_score(self, domain, features):
        config = self.DOMAIN_MATRIX[domain]
        weights = dict(config["weights"])
        sigma = config["sigma"]
        if domain == "Parkinson" and features.get("is_refractory", False):
            weights["vol"] = 0.45
            weights["aca"] = 0.05
        final_score = 0
        for key, w in weights.items():
            f_val = features.get(key, 0.5)
            final_score += sigma * math.log(1 + w * f_val)
        noise = random.uniform(-0.015, 0.015)
        return round(final_score + noise, 4)

    def generate_decision_report(self, domain, score, query=""):
        """输出系统决策状态 — 全部节点重构为 AGID 体系。"""
        threshold = self.DOMAIN_MATRIX[domain]["min_threshold"]
        status = "PASSED" if score >= threshold else "REJECTED"
        report_id = to_agid("AMAH", "REPORT", f"{domain}:{score}:{status}")
        return {
            "agid": report_id,
            "domain": domain,
            "composite_score": score,
            "threshold": threshold,
            "decision": status,
            "d_precision": min(1.0, score),
        }

    def process_with_entropy(self, query, features):
        """V4.0：带波形熵检测与 variance>0.005 物理拦截的流程。"""
        _, variance = calculate_sliding_entropy(query)
        if variance > VARIANCE_INTERCEPT_THRESHOLD:
            return {
                "agid": to_agid("AMAH", "INTERCEPT", f"var_{variance:.6f}"),
                "decision": "REJECTED",
                "reason": "variance_physical_intercept",
                "variance": variance,
            }
        domain = self.detect_strategic_domain(query)
        score = self.calculate_nonlinear_score(domain, features)
        return self.generate_decision_report(domain, score, query)


if __name__ == "__main__":
    orchestrator = AMAHWeightOrchestrator()
    mock_query = "Refractory Parkinson's patient, STN-DBS placement"
    mock_features = {"vol": 0.9, "aca": 0.6, "pi": 1.0, "inst": 0.8, "rep": 0.7, "is_refractory": True}
    out = orchestrator.process_with_entropy(mock_query, mock_features)
    print(f"📊 AMAH V4.0 输出 (AGID):\n{json.dumps(out, indent=4)}")
