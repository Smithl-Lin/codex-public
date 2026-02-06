# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
# Billing Engine V4.0 — 挂载 D ≤ 0.79 联动，AGID 输出体系

import json
import hashlib

# ------------------------------------------------------------------------------
# AGID 体系
# ------------------------------------------------------------------------------
def to_agid(namespace: str, node_type: str, raw_id) -> str:
    sid = hashlib.sha256(f"{namespace}:{node_type}:{raw_id}".encode()).hexdigest()[:12].upper()
    return f"AGID-{namespace}-{node_type}-{sid}"


# V4.0 硬性指标：精度距离 D 阈值，D ≤ 0.79 时允许计费联动
D_PRECISION_THRESHOLD = 0.79


class AMAHBillingEngine:
    def __init__(self):
        self.BASE_AUDIT_FEE = 500.0
        self.SUB_TIERS = {
            "TRINITY_FULL": 299.0,
            "DEGRADED_DUAL": 149.0,
            "STRATEGIC_VETO": 0.0
        }
        self.ADDON_PRICING = {
            "Hospital Docking": 2500.0,
            "Travel Concierge": 1200.0,
            "Insurance Liaison": 850.0,
            "Remote Consultation": 450.0,
            "Genetic Counseling": 600.0
        }
        self.D_THRESHOLD = D_PRECISION_THRESHOLD

    def generate_quote(self, score, mode, services_list, d_precision=None):
        """
        根据匹配精度与服务深度生成商业报价单。
        V4.0: 挂载 billing_engine 与 D ≤ 0.79 联动 — 仅当 D ≤ 0.79 时启用计费。
        """
        # 使用精度距离 D（未传入时用 score 近似）
        D = d_precision if d_precision is not None else (score if score is not None else 0.0)
        # D ≤ 0.79 联动：满足条件时 effective_score 取 score，否则不计费
        effective_score = score if (score and D <= self.D_THRESHOLD and score >= 0.79) else 0.0

        core_matching_fee = self.BASE_AUDIT_FEE * effective_score
        sub_fee = self.SUB_TIERS.get(mode, 100.0) if effective_score > 0 else 0.0

        if isinstance(services_list, str):
            try:
                services = json.loads(services_list)
            except Exception:
                services = []
        else:
            services = services_list or []

        addon_total = sum([self.ADDON_PRICING.get(s, 500.0) for s in services])
        total_quote = core_matching_fee + sub_fee + addon_total

        quote_id = to_agid("BILL", "QUOTE", f"{effective_score}:{total_quote}")
        return {
            "agid": quote_id,
            "status": "SUCCESS" if effective_score > 0 else "REJECTED_BY_ACCURACY",
            "d_precision": D,
            "d_threshold": self.D_THRESHOLD,
            "d_linked": D <= self.D_THRESHOLD,
            "total_quote": round(total_quote, 2),
            "breakdown": {
                "base_audit_purchase": round(core_matching_fee, 2),
                "subscription_monthly": sub_fee,
                "value_added_services_total": round(addon_total, 2)
            },
            "matched_services": services,
            "currency": "USD"
        }

    def print_invoice_demo(self, quote_data):
        print("\n" + "="*40)
        print("      AMAH PLATFORM V4.0 - STRATEGIC INVOICE")
        print("="*40)
        print(f"AGID: {quote_data.get('agid', 'N/A')} | D≤0.79 联动: {quote_data.get('d_linked', False)}")
        if quote_data["status"] == "SUCCESS":
            print(f"Status:       HIGH_PRECISION_MATCHED (D={quote_data.get('d_precision', 'N/A')})")
            print(f"Total Amount: {quote_data['total_quote']} {quote_data['currency']}")
            print("-" * 40)
            print(f"- Audit Purchase: ${quote_data['breakdown']['base_audit_purchase']}")
            print(f"- Subscription:   ${quote_data['breakdown']['subscription_monthly']}")
            print(f"- Add-on Total:   ${quote_data['breakdown']['value_added_services_total']}")
            print(f"Services included: {', '.join(quote_data['matched_services'])}")
        else:
            print("Status:       STRATEGIC_REJECTED")
            print("Reason:       D > 0.79 or accuracy below threshold. No charge.")
        print("="*40 + "\n")


if __name__ == "__main__":
    engine = AMAHBillingEngine()
    demo_services = ["Hospital Docking", "Travel Concierge"]
    quote = engine.generate_quote(score=0.92, mode="TRINITY_FULL", services_list=demo_services, d_precision=0.75)
    engine.print_invoice_demo(quote)
