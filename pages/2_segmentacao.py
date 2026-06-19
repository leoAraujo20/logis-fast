import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st


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

    recommendations = {
        0: "Reduzir cupons — compra mesmo sem desconto agressivo.",
        1: "Manter engajamento com fidelidade, não com cupom.",
        2: "Oferecer experiência premium e frete grátis.",
        3: "Campanhas de reativação com cupons pontuais.",
    }

    profile["Perfil"] = profile["Cluster"].map(names)
    profile["Recomendacao"] = profile["Cluster"].map(recommendations)
    return profile


st.title("🎯 Segmentação de Clientes (K-Means)")

df_seg = load_segmented_data()
profile = get_cluster_profile(df_seg)

st.subheader("📊 Perfis de Consumo Identificados")
cols = st.columns(4)

for i, row in profile.iterrows():
    with cols[i]:
        colors = {
            0: {"bg": "#E3F2FD", "border": "#00b4d8", "text": "#01579B"},
            1: {"bg": "#FCE4EC", "border": "#f72585", "text": "#880E4F"},
            2: {"bg": "#F3E5F5", "border": "#7209b7", "text": "#4A148C"},
            3: {"bg": "#E8F5E9", "border": "#43aa8b", "text": "#1B5E20"},
        }
        c = colors.get(i, {"bg": "#f0f2f6", "border": "#7209b7", "text": "#333"})

        st.markdown(
            f"""
        <div style="
            background-color: {c["bg"]}; 
            padding: 20px; 
            border-radius: 15px; 
            border-top: 8px solid {c["border"]}; 
            height: 300px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1);
            color: {c["text"]};
        ">
            <h3 style="margin-top: 0; color: {c["text"]}; text-align: center; font-size: 1.2em;">{row["Perfil"]}</h3>
            <hr style="border: 0; border-top: 1px solid rgba(0,0,0,0.1); margin: 10px 0;">
            <div style="font-size: 0.95em; line-height: 1.6;">
                <p><b>📦 Frequência:</b> {row["frequencia"]:.1f} pedidos</p>
                <p><b>💰 Ticket:</b> R$ {row["ticket_medio"]:.2f}</p>
                <p><b>🎟️ Uso Cupom:</b> {row["taxa_uso_cupom"]:.1f}%</p>
            </div>
            <div style="
                margin-top: 15px; 
                padding: 10px; 
                background-color: rgba(255,255,255,0.5); 
                border-radius: 8px;
                font-size: 0.85em;
                font-style: italic;
                border-left: 3px solid {c["border"]};
            ">
                <b>Estratégia:</b> {row["Recomendacao"]}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

row1_col1, row1_col2 = st.columns([2, 1])

with row1_col1:
    st.subheader("🌀 Visualização dos Clusters (PCA)")
    st.write("Redução de 4 dimensões para 2 componentes principais.")

    names_map = {0: "Caçador", 1: "Fiel", 2: "Alto Valor", 3: "Casual"}
    df_seg["Perfil_Resumido"] = df_seg["Cluster"].map(names_map)

    fig_pca = px.scatter(
        df_seg,
        x="PCA1",
        y="PCA2",
        color="Perfil_Resumido",
        hover_data=["User_ID", "City", "frequencia", "ticket_medio"],
        color_discrete_map={
            "Caçador": "#00b4d8",
            "Fiel": "#f72585",
            "Alto Valor": "#7209b7",
            "Casual": "#43aa8b",
        },
        title="Dispersão de Clientes",
        labels={"Perfil_Resumido": "Perfil"},
    )
    st.plotly_chart(fig_pca, use_container_width=True)

with row1_col2:
    st.subheader("📍 Presença Geográfica")
    city_dist = (
        df_seg.groupby(["City", "Perfil_Resumido"])
        .size()
        .reset_index(name="Quantidade")
    )

    fig_geo = px.bar(
        city_dist,
        y="City",
        x="Quantidade",
        color="Perfil_Resumido",
        orientation="h",
        barmode="stack",
        color_discrete_map={
            "Caçador": "#00b4d8",
            "Fiel": "#f72585",
            "Alto Valor": "#7209b7",
            "Casual": "#43aa8b",
        },
        labels={"Perfil_Resumido": "Perfil"},
    )
    st.plotly_chart(fig_geo, use_container_width=True)
