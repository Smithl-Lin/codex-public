# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
import asyncio
from amani_core_v4 import AMANICoreOrchestrator

PROFILE = """Patient: 62yo Male. Diagnosis: Advanced PD with significant motor fluctuations. Genetic screen shows GBA mutation. Previous medications: Levodopa (ineffective), Amantadine. Seeking advanced neuromodulation. Primary requirement: Subthalamic Nucleus (STN) Deep Brain Stimulation (DBS) with directional leads. Location: Priority Jacksonville, FL (JAX)."""

async def main():
    orch = AMANICoreOrchestrator()
    result = await orch.execute_global_match(PROFILE)
    print("=== AMANI V4.0 Global Match Result ===")
    print("Status:", result.get("status"))
    print("AGID:", result.get("agid"))
    if result.get("precision") is not None:
        print("Precision (D):", result.get("precision"))
    if result.get("commercial_value") is not None:
        print("Commercial value (shadow):", result.get("commercial_value"))
    if result.get("reason"):
        print("Reason:", result.get("reason"))

if __name__ == "__main__":
    asyncio.run(main())
