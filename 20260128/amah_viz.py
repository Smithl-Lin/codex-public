import streamlit as st
import pandas as pd
import json
import pydeck as pdk
import numpy as np
import time
import chromadb
import os
from fpdf import FPDF

# --- 1. 专利 1：硬化递进式引擎 ---
class AMAHPatentEngine:
    @staticmethod
    def apply_staircase_logic(metadata, query):
        q_up = query.upper()
        vol = metadata.get('vol_score', 0.5)
        # 硬性提权：针对转移、难治性等临床红区执行 2.5x 增益
        hard_boost = 2.5 if any(kw in q_up for kw in ["转移", "META", "难治性", "REFRACTORY", "RET", "ADC"]) else 1.0
        
        if ("DBS" in q_up or "SURGERY" in q_up) and vol >= 0.6:
            label, mult = "Gold Standard (金标准)", 1.5
            dep = "Path Locked: 已锚定高成熟度金标准术式方案。"
        elif hard_boost > 1.0 or metadata.get('is_pi'):
            label, mult = "Frontier Tech (前哨技术)", 2.2 # 专利 1 创新溢价
            dep = "Strategic Alert: 识别到复杂诉求，已启动前哨技术与 PI 级专家对位。"
        else:
            label, mult = "Recovery (辅助康复)", 1.1
            dep = "Staging: 常规随访与基础健康管理路径。"
            
        return label, (hard_boost * mult), dep

# --- 2. 语义净化器 (PDF 稳定性核心) ---
def sanitize_for_pdf(text):
    """最稳健的字符过滤：将非 Latin-1 字符替换为安全描述，防止 PDF 引擎崩溃"""
    replacements = {"金标准": "Gold Standard", "前哨技术": "Frontier Tech", "辅助康复": "Recovery", "🔒": "[LOCKED]", "⚠️": "[ALERT]"}
    for k, v in replacements.items():
        text = text.replace(k, v)
    # 彻底清除所有非 ASCII 字符以保命
    return "".join([c if ord(c) < 128 else "?" for c in text])

# --- 3. UI 与 数据底座 ---
st.set_page_config(layout="wide", page_title="AMAH Strategic Intelligence")

@st.cache_resource
def get_chroma():
    return chromadb.PersistentClient(path="./amah_vector_db")

@st.cache_data
def load_nebula():
    with open('nebula_data.json', 'r') as f: return pd.DataFrame(json.load(f))

# 初始化
df_nebula = load_nebula()
client = get_chroma()
collection = client.get_collection("expert_map_global")

st.title("🚀 AMAH 全球医疗资源战略决策中心 (V27.0)")
st.markdown("---")

# 中心搜索功能恢复
st.subheader("🧬 患者诉求查询 (Patient Demand Query)")
user_input = st.text_area("在此输入患者具体临床诉求：", placeholder="例如：肺癌脑转移，寻求前哨技术对位...", height=100)
domain = st.selectbox("核心医疗领域锁定", ["Oncology", "Parkinson (PD)", "TBI", "BCI", "Longevity", "Neurostimulation"])
execute = st.button("🔴 启动硬性提权匹配", type="primary")

if execute and user_input:
    # 动态热力图动图演示
    map_p = st.empty()
    for i in range(1, 4):
        d = df_nebula.sample(int(len(df_nebula)*(i/3)))
        map_p.pydeck_chart(pdk.Deck(layers=[pdk.Layer("HeatmapLayer", d, get_position='[lng, lat]', radius_pixels=35)], 
                                  initial_view_state=pdk.ViewState(latitude=30.33, longitude=-81.65, zoom=3)))
        time.sleep(0.1)

    # 检索与专利对位
    results = collection.query(query_texts=[user_input], n_results=10)
    final_list = []
    engine = AMAHPatentEngine()
    
    for i in range(len(results['ids'][0])):
        meta = results['metadatas'][0][i]
        label, total_mult, dep = engine.apply_staircase_logic(meta, user_input)
        # 综合分值 = (0.5*手术量 + 0.5*PI身份) * 专利倍率
        base_score = (0.5 * meta.get('vol_score', 0.5) + 0.5 * (1.0 if meta.get('is_pi') else 0))
        final_score = round(base_score * total_mult, 4)
        
        final_list.append({
            "name": meta.get('name', f"Expert_{results['ids'][0][i][:6]}"),
            "label": label, "score": final_score, "hub": meta.get('hub', 'Medical Center'), "dep": dep
        })
    
    final_list = sorted(final_list, key=lambda x: x['score'], reverse=True)[:3]
    
    # UI 输出
    st.info(f"🧬 AMAH 路径建议: {final_list[0]['dep']}")
    cols = st.columns(3)
    for idx, exp in enumerate(final_list):
        with cols[idx]:
            status = "LOCKED" if exp['score'] >= 0.85 else "DISPUTED"
            st.markdown(f"**[{exp['label']}]**")
            st.success(f"{status}: {exp['name']}\n\n分值: {exp['score']}\n\n中心: {exp['hub']}")

    # --- 终极稳定 PDF 导出逻辑 ---
    st.markdown("---")
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, sanitize_for_pdf("AMAH Strategic Staging Report"), ln=True, align='C')
        pdf.ln(10)
        pdf.multi_cell(0, 10, sanitize_for_pdf(f"Clinical Inquiry: {user_input}"))
        pdf.ln(5)
        for e in final_list:
            line = f"- {e['name']} | {e['label']} | Score: {e['score']}"
            pdf.cell(200, 10, sanitize_for_pdf(line), ln=True)
            
        st.download_button("📥 下载完整决策报告 (PDF)", data=bytes(pdf.output()), file_name="AMAH_Report.pdf", mime="application/pdf")
    except Exception as ex:
        st.error(f"PDF 引擎错误: {ex}")

else:
    st.info("💡 请输入高精度诉求以触发专利 1 的战略提权机制。")
