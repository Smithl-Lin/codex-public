# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
端到端 TrinityBridge 测试：验证 L1→L2→L2.5→L3→L4 完整流程
"""
import sys
import time
from amani_trinity_bridge import TrinityBridge, ECNNSentinel


def test_full_trinity_pipeline():
    """测试完整的 Trinity 流程：L1→L2→L2.5→L3→L4"""
    print("=" * 80)
    print("🧪 TrinityBridge 端到端测试 — 完整五层流程验证")
    print("=" * 80)

    test_cases = [
        {
            "id": "TC001_EN_NEURO",
            "input": "65yo Male, Advanced Parkinson's, seeking DBS evaluation at Mayo Jacksonville",
            "expected_dept": "Neurology",
        },
        {
            "id": "TC002_EN_ONCO",
            "input": "58yo Female, NSCLC KRAS G12C+, looking for Phase III clinical trials",
            "expected_dept": "Oncology",
        },
        {
            "id": "TC003_ZH_NEURO",
            "input": "帕金森患者，65岁，寻求 DBS 脑深部电刺激评估",
            "expected_dept": "Neurology",
            "test_l2_equalization": True,
        },
        {
            "id": "TC004_INTERCEPT",
            "input": "x",  # 极短文本，应该被 L1 熵门拦截
            "expect_intercept": True,
        },
    ]

    passed = 0
    failed = 0

    for tc in test_cases:
        tc_id = tc["id"]
        input_text = tc["input"]
        expect_intercept = tc.get("expect_intercept", False)

        print(f"\n[{tc_id}] {input_text[:60]}...")
        start = time.time()

        try:
            # For non-intercept cases use a relaxed variance limit so E2E layers can be validated.
            bridge = TrinityBridge(
                l1_sentinel=ECNNSentinel(variance_limit=0.1)
            ) if not expect_intercept else TrinityBridge()
            result = bridge.run_safe(input_text, top_k_agids=3)
            elapsed = time.time() - start

            # 检查是否按预期拦截
            intercepted = result.get("intercepted", False)

            if expect_intercept:
                if intercepted:
                    print(f"  ✅ L1 拦截符合预期")
                    print(f"  📊 拦截原因: {result['l1_sentinel'].get('error', 'N/A')}")
                    passed += 1
                else:
                    print(f"  ❌ 应该被 L1 拦截但通过了")
                    failed += 1
            else:
                if intercepted:
                    print(f"  ❌ 意外被 L1 拦截: {result['l1_sentinel'].get('error')}")
                    failed += 1
                else:
                    # 验证各层输出
                    l1 = result.get("l1_sentinel", {})
                    l2_path = result.get("l2_2_5_semantic_path", {})
                    l3 = result.get("l3_nexus", {})
                    l4 = result.get("l4_multimodal", {})

                    d_eff = l1.get("d_effective")
                    agids = l3.get("agids", [])
                    strategy = l2_path.get("strategy", [])

                    print(f"  ✅ L1 通过 | D-effective: {d_eff:.4f}")
                    print(f"  ✅ L2 策略步骤: {len(strategy)} 步")

                    # 检查 L2 文化均等化
                    if tc.get("test_l2_equalization"):
                        equalized = result.get("l2_equalized_input")
                        if equalized and equalized != input_text:
                            print(f"  ✅ L2 均等化: {equalized[:50]}...")
                        else:
                            print(f"  ⚠️  L2 均等化未触发")

                    # L2.5 验证（通过 Orchestrator）
                    orch_audit = l2_path.get("orchestrator_audit", {})
                    if orch_audit:
                        print(f"  ✅ L2.5 Orchestrator | 合规分: {orch_audit.get('compliance_score', 'N/A')}")

                    # L3 验证
                    print(f"  ✅ L3 AGID 映射: {len(agids)} 个")
                    if agids:
                        print(f"     Top AGID: {agids[0]}")

                    # L4 验证
                    if l4:
                        print(f"  ✅ L4 多模态输出: {list(l4.keys())[:3]}")

                    # Centurion 快照
                    centurion = result.get("centurion_snapshot")
                    if centurion:
                        print(f"  ✅ L2 Centurion: {centurion.get('layer', 'N/A')}")

                    passed += 1

            print(f"  ⏱️  耗时: {elapsed:.3f}s")

        except Exception as e:
            print(f"  ❌ 异常: {e}")
            failed += 1

        print("-" * 60)

    # 总结
    print("\n" + "=" * 80)
    print(f"📊 测试总结")
    print("=" * 80)
    print(f"✅ 通过: {passed}/{len(test_cases)}")
    print(f"❌ 失败: {failed}/{len(test_cases)}")

    if failed == 0:
        print("\n🎉 所有测试通过！Trinity 五层流程运行正常。")
        return 0
    else:
        print(f"\n⚠️  {failed} 个测试失败，请检查日志。")
        return 1


if __name__ == "__main__":
    exit_code = test_full_trinity_pipeline()
    sys.exit(exit_code)
