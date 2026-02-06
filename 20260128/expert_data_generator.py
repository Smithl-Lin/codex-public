import json

# V10.3: 极致硬化版本 - 消除语义噪声
# 重点：将专家信息转化为“高维特征指纹”
high_fidelity_experts = [
    {
        "id": "exp_jax_001_v3",
        "name": "Dr. Smith (Mayo JAX)",
        "affiliation": "Mayo Clinic Jacksonville Florida",
        "specialty": "Neuromodulation",
        # 极简且高密的特征描述
        "expertise_tags": ["STN-DBS", "Parkinson", "Florida", "Jacksonville", "DBS-Lead", "Stereotactic"],
        "insurance_partners": ["Medicare", "BlueCross"],
        "value_add_services": ["Travel-Concierge", "Hospital-Docking"],
        "location": {"city": "Jacksonville", "state": "Florida", "zip": "32224"}
    }
]

# 模拟库中其他干扰数据，保持 50 个节点的检索压力
for i in range(101, 150):
    high_fidelity_experts.append({
        "id": f"exp_bulk_{i}",
        "name": f"Expert_{i}",
        "affiliation": "Other Clinic",
        "specialty": "General Medicine",
        "expertise_tags": ["Internal-Medicine"],
        "insurance_partners": ["None"],
        "value_add_services": ["Standard"],
        "location": {"city": "Unknown", "state": "US", "zip": "00000"}
    })

with open('expert_map_data.json', 'w') as f:
    json.dump(high_fidelity_experts, f, indent=2)

print("🚀 V10.3 核心语义硬化数据已生成。")
