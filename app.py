import streamlit as st

st.set_page_config(page_title="LogisFast Dashboard", page_icon="🚚", layout="wide")

# Definição das páginas
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

# Configuração da navegação
pg = st.navigation(pages)
pg.run()

# Rodapé comum
st.sidebar.markdown("---")
st.sidebar.markdown("developed by **LogisFast Team**")
