# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
# App V4.0 — 统一走 amani_core_v4 配置与 AGID，0.79 阈值闭环

import pandas as pd

# 闭环：阈值与 AGID 仅来自 amani_core_v4 与 amah_config.json
from amani_core_v4 import (
    load_config,
    get_precision_threshold,
    get_manual_audit_threshold,
    to_agid,
)

D_PRECISION_THRESHOLD = get_precision_threshold()
D_MANUAL_AUDIT = get_manual_audit_threshold()

try:
    import streamlit as st
except ImportError:
    st = None

try:
    from billing_engine import AMAHBillingEngine
    _billing = AMAHBillingEngine()
except Exception:
    _billing = None


def _bridge_result_to_routing(result, query_text: str, default_threshold: float):
    """Map TrinityBridge.run_safe result to routing UI payload (English-only)."""
    if result.get("intercepted"):
        return "Intercepted", None, result.get("l1_sentinel", {}).get("error", "L1 intercepted"), {
            "steps": [("Step 0: L1 Gate", "Request blocked by entropy/D threshold.")],
            "experts": pd.DataFrame(columns=["AGID", "Score"]),
        }
    l1 = result.get("l1_sentinel") or {}
    l2 = result.get("l2_2_5_semantic_path") or {}
    l3 = result.get("l3_nexus") or {}
    D = l1.get("d_effective") or default_threshold
    agids = l3.get("agids") or []
    scores = l3.get("scores") or []
    agid = agids[0] if agids else to_agid("ROUTE", "AUDIT", f"D_{D:.2f}")
    strategy = l2.get("strategy") or []
    steps = [(f"Step {s.get('sequence', i)}: {s.get('category', '')}", s.get("stage", "")) for i, s in enumerate(strategy, 1)]
    if not steps:
        steps = [
            ("Step 1: Gold Standard", "Trinity staircase strategy."),
            ("Step 2: Frontier", "L3 AGID anchoring."),
            ("Step 3: Recovery", "Physical routing & delivery."),
        ]
    q = (query_text or "").lower()
    if any(k in q for k in ["parkinson", "dbs", "bci", "脑", "帕金森"]):
        dept = "Neurology"
    elif any(k in q for k in ["癌", "瘤", "肿", "cancer", "metastasis"]):
        dept = "Oncology"
    else:
        dept = (strategy[0].get("category") if strategy else None) or "Complex-Cases"
    experts = (
        pd.DataFrame({"AGID": agids[:10], "Score": scores[:10]})
        if agids
        else pd.DataFrame({"AGID": [agid], "Score": [D]})
    )
    return dept, D, agid, {"steps": steps, "experts": experts}


def get_strategic_routing(query):
    """Deprecated routing. Enforced to use TrinityBridge.run_safe for L1 gate closure."""
    try:
        import os
        from amani_nexus_layer_v3 import get_default_router
        base = os.path.dirname(os.path.abspath(__file__))
        get_default_router(os.path.join(base, "physical_node_registry.json"))
    except Exception:
        pass
    try:
        from amani_trinity_bridge import TrinityBridge
        bridge = TrinityBridge()
        result = bridge.run_safe(query or " ", top_k_agids=5)
    except Exception as e:
        result = {"intercepted": True, "l1_sentinel": {"passed": False, "error": str(e)}}
    return _bridge_result_to_routing(result, query, D_PRECISION_THRESHOLD)

if st is not None:
    st.set_page_config(page_title="Mayo AI Asset Hub V4 | Smith Lin", layout="wide")
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; }
        div[data-testid="stMetricDelta"] { background-color: #D1FAE5 !important; color: #064E3B !important; padding: 5px 12px; border-radius: 8px; font-weight: 800; }
        .report-card { background: #FFFFFF; border: 2px solid #E5E7EB; border-left: 8px solid #005EB8; border-radius: 12px; padding: 25px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); position: relative; }
        .ver-stamp { position: absolute; top: 20px; right: 20px; border: 3px solid #DC2626; color: #DC2626; padding: 6px 15px; border-radius: 6px; font-weight: 900; transform: rotate(-5deg); text-transform: uppercase; }
        .step-box { background-color: #F8FAFC; border-radius: 10px; padding: 15px; margin: 12px 0; border: 1px solid #E2E8F0; }
        .perfect-match { color: #FFFFFF; background-color: #10B981; padding: 4px 12px; border-radius: 6px; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<h2 style='color: #005EB8;'>🏥 调度指挥中心 V4.0</h2>", unsafe_allow_html=True)
        st.metric(label="🌍 实时活跃资产总数", value="19,824", delta="+9 今日新增 (Live)")
        st.progress(0.79, text="Q1 资产覆盖进度: 79%")
        st.markdown(f"**0.79 阈值来源:** amah_config.json (闭环)")
        st.markdown(f"**D≤{D_PRECISION_THRESHOLD} 计费联动:** 已启用")
        st.markdown(f"**验证专家:** Dr. Smith Lin Mayo Jacksonville")

    st.markdown("<h1 style='color: #005EB8;'>全球医疗资产调度与 AI 审计引擎 (V4.0 闭环)</h1>", unsafe_allow_html=True)
    patient_input = st.text_area("请输入画像需求 (阈值来自 amah_config.json):", height=150, placeholder="例如：65yo Male, Advanced Parkinson's...")

    if st.button("🚀 启动 5.0x 本体论深度对位", type="primary"):
        dept, D, agid, config = get_strategic_routing(patient_input)
        d_linked = D <= D_PRECISION_THRESHOLD

        st.markdown(f"""
        <div class="report-card">
            <div class="ver-stamp">MAYO V4.0</div>
            <h2 style="color: #005EB8; margin: 0;">Mayo AI Strategic Audit</h2>
            <p style="margin-top: 15px;">
                <b>AGID:</b> <code>{agid}</code><br>
                <b>学科对位:</b> {dept} |
                <b>Precision Distance D:</b> <span class="{'perfect-match' if D <= 0.8 else ''}">{D:.2f}</span>
                <b>D≤{D_PRECISION_THRESHOLD} 计费联动:</b> {'✅ 已启用' if d_linked else '❌ 未启用'}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🔄 递进式个性化策略建议")
        for title, content in config["steps"]:
            st.markdown(f"<div class='step-box'><b>{title}</b><br>{content}</div>", unsafe_allow_html=True)

        st.markdown(f"### 🗺️ 全美核心 {dept} 中心与专家智库")
        st.table(config["experts"])

        if _billing and D <= D_PRECISION_THRESHOLD:
            quote = _billing.generate_quote(score=min(1.0, 1.2 - D), mode="TRINITY_FULL", services_list=["Hospital Docking", "Travel Concierge"], d_precision=D)
            total_quote = quote.get("total_quote", 0)
            st.markdown(f"""
                <div style='background:#FEFCE8; padding:15px; border-radius:10px; border: 1px solid #FDE68A; margin-top: 20px;'>
                    <b style='color: #854D0E;'>💰 影子账单 (D≤{D_PRECISION_THRESHOLD} 联动): ${total_quote:,.0f} | AGID: {quote.get('agid', 'N/A')}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style='background:#FEFCE8; padding:15px; border-radius:10px; border: 1px solid #FDE68A; margin-top: 20px;'>
                    <b style='color: #854D0E;'>💰 影子账单: D > {D_PRECISION_THRESHOLD} 时不计费 (amah_config.json 闭环)</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

else:
    if __name__ == "__main__":
        r = get_strategic_routing("Parkinson DBS")
        print("V4.0 gated routing:", r[0], r[1], r[2])
