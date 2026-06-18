import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px


def load_segmented_data():
    conn = sqlite3.connect("logisfast.db")
    df = pd.read_sql_query("SELECT * FROM CLIENTES_SEGMENTADOS", conn)
    conn.close()
    return df


def get_cluster_profile(df):
    features = ["frequencia", "ticket_medio", "tempo_entrega_medio", "taxa_uso_cupom"]
    profile = df.groupby("Cluster")[features].mean().reset_index()

    names = {
        0: "🎯 Caçador de Promoção",
        1: "💎 Cliente Fiel",
        2: "👑 Alto Valor",
        3: "😐 Cliente Casual",
    }
    profile["Perfil"] = profile["Cluster"].map(names)
    return profile


st.title("🎯 Segmentação de Clientes (K-Means)")

df_seg = load_segmented_data()
profile = get_cluster_profile(df_seg)

st.subheader("Perfis Identificados")
cols = st.columns(4)

for i, row in profile.iterrows():
    with cols[i]:
        st.info(f"**{row['Perfil']}**")
        st.write(f"Freq: {row['frequencia']:.1f} ped.")
        st.write(f"Ticket: R$ {row['ticket_medio']:.2f}")
        st.write(f"Cupom: {row['taxa_uso_cupom']:.1f}%")

st.markdown("---")

st.subheader("Distribuição Espacial dos Clusters (PCA)")
st.write(
    "Redução de 4 dimensões (Frequência, Ticket, Tempo, Cupom) para 2 componentes principais."
)

fig_pca = px.scatter(
    df_seg,
    x="PCA1",
    y="PCA2",
    color="Cluster",
    hover_data=["User_ID", "City", "frequencia", "ticket_medio"],
    color_continuous_scale="Viridis",
    title="Visualização PCA dos Clusters",
)
st.plotly_chart(fig_pca, width='stretch')

st.subheader("Distribuição Geográfica por Cluster")
fig_geo = px.histogram(
    df_seg,
    x="City",
    color="Cluster",
    barmode="group",
    color_discrete_sequence=px.colors.qualitative.Plotly,
)
st.plotly_chart(fig_geo, width='stretch')
