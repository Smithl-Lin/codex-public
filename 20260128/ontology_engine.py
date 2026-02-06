# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
# Ontology Engine V4.0 — AGID 输出体系

import hashlib

# ------------------------------------------------------------------------------
# AGID 体系
# ------------------------------------------------------------------------------
def to_agid(namespace: str, node_type: str, raw_id) -> str:
    sid = hashlib.sha256(f"{namespace}:{node_type}:{raw_id}".encode()).hexdigest()[:12].upper()
    return f"AGID-{namespace}-{node_type}-{sid}"


MEDICAL_ONTOLOGY = {
    "Parkinson": {
        "boost_keywords": ["iPS", "BCI", "Dopaminergic", "Subthalamic", "Neural Interface", "Neuralink"],
        "boost_weight": 5.0,
        "must_have": ["iPS", "BCI", "DBS"],
        "exclusion": ["Mechanical Ventilation", "ICU", "Nursing Care"]
    },
    "Cancer": {
        "boost_keywords": ["KRAS", "G12C", "mRNA Vaccine", "CAR-T", "ADC"],
        "boost_weight": 4.0,
        "exclusion": ["Palliative Care"]
    }
}


def enhance_query_with_ontology(original_query):
    """V4.0: 输出节点重构为 AGID 体系。"""
    enhanced_query = original_query
    active_rules = []
    hard_anchors = []

    for disease, rules in MEDICAL_ONTOLOGY.items():
        if disease.lower() in original_query.lower() or "帕金森" in original_query:
            active_rules.append(disease)
            tech_injection = " ".join([f"{k}" for k in rules["boost_keywords"]] * int(rules["boost_weight"]))
            enhanced_query += f" {tech_injection}"
            for anchor in ["iPS", "BCI", "DBS", "脑机接口", "干细胞"]:
                if anchor.lower() in original_query.lower():
                    hard_anchors.append(anchor)

    # AGID: 增强结果输出节点
    agid_enhance = to_agid("ONT", "ENHANCE", f"{original_query[:30]}:{','.join(active_rules)}")
    return enhanced_query, active_rules, hard_anchors, agid_enhance
