# 文件名: medical_kg.py
import json

def get_us_precision_knowledge():
    """
    定义美国最新的精准医疗知识图谱节点
    包含：基因靶点 -> 关联癌种 -> 美国FDA已批准/在研药物
    """
    kg = {
        "KRAS G12C": {
            "disease": ["NSCLC", "Colorectal Cancer"],
            "approved_drugs": ["Sotorasib (Lumakras)", "Adagrasib (Krazati)"],
            "related_pathways": "MAPK Signaling",
            "clinical_relevance": "High-Value Target in US Precision Oncology"
        },
        "EGFR Exon 19 del": {
            "disease": ["NSCLC"],
            "approved_drugs": ["Osimertinib", "Gefitinib"],
            "related_pathways": "ErbB Signaling",
            "clinical_relevance": "Standard of Care for Targeted Therapy"
        },
        "HER2 Positive": {
            "disease": ["Breast Cancer", "Gastric Cancer"],
            "approved_drugs": ["Trastuzumab", "T-DXd (Enhertu)"],
            "related_pathways": "RTK Signaling",
            "clinical_relevance": "Gold Standard for Antibody-Drug Conjugates (ADC)"
        }
    }
    return kg

def build_kg_index():
    kg = get_us_precision_knowledge()
    # 将知识图谱保存为本地 JSON，供推理机调用
    with open("precision_kg.json", "w", encoding="utf-8") as f:
        json.dump(kg, f, ensure_ascii=False, indent=2)
    print("✅ 美国精准医疗知识图谱已构建完成 (JSON Layer)。")

if __name__ == "__main__":
    build_kg_index()