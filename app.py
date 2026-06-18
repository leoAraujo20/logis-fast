import streamlit as st

st.set_page_config(page_title="LogisFast Dashboard", page_icon="🚚", layout="wide")

pages = {
    "Principal": [
        st.Page("pages/1_visao_geral.py", title="📊 Visão Geral", icon="📈"),
        st.Page(
            "pages/2_segmentacao.py", title="🎯 Segmentação de Clientes", icon="👥"
        ),
    ],
    "Dados": [
        st.Page("pages/3_dados_brutos.py", title="📋 Dados Brutos", icon="📁"),
    ],
}

pg = st.navigation(pages)
pg.run()

st.sidebar.markdown("---")
st.sidebar.subheader("🚚 LogisFast")
st.sidebar.write("""
Este dashboard apresenta uma análise detalhada da operação logística, 
incluindo KPIs de entrega e segmentação de clientes via Inteligência Artificial.
""")
st.sidebar.markdown("developed by **LogisFast Team**")
