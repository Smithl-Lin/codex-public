import streamlit as st
import asyncio
from amah_unified_synergy import AMAHUnifiedSynergy

st.set_page_config(page_title="AMAH Strategic Portal", layout="wide")

st.title("🛡️ AMAH: 医疗资产与全周期管理平台")
st.subheader("基于 2026 多模型博弈引擎的决策与计费系统")

query = st.text_input("请输入患者诉求 (例如: Parkinson DBS needs in Florida):", 
                     "Need urgent high-precision DBS lead placement for Parkinson patient, Florida, Medicare required.")

if st.button("启动全球资源对位"):
    pipeline = AMAHUnifiedSynergy()
    
    with st.spinner('正在检索全美资产库并启动三路模型博弈...'):
        # 运行异步逻辑
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        quote = loop.run_until_complete(pipeline.execute_strategic_matching(query))
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("✅ 战略匹配达成")
        st.json(quote['breakdown'])
        
    with col2:
        st.metric("预估总报价 (USD)", f"${quote['total_quote']}")
        st.write("已激活服务:", ", ".join(quote['matched_services']))

st.sidebar.info(f"当前节点: Jacksonville, FL\n用户状态: J-1 Research Fellow (Dr. Lin)")
