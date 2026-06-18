import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px


def load_data():
    conn = sqlite3.connect("logisfast.db")
    query = """
        SELECT P.*, C.City, C.Payment_Method 
        FROM PEDIDOS P 
        JOIN CLIENTES C ON P.User_ID = C.User_ID
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


st.title("📊 Visão Geral da Operação")

df = load_data()

# Sidebar: Filtros e Informações
st.sidebar.header("⚙️ Filtros")
cidades = st.sidebar.multiselect(
    "Selecione as Cidades", options=sorted(df["City"].unique()), default=df["City"].unique()
)

status = st.sidebar.multiselect(
    "Status do Pedido", options=df["Order_Status"].unique(), default=df["Order_Status"].unique()
)

df_filtered = df[(df["City"].isin(cidades)) & (df["Order_Status"].isin(status))]

# Métricas Principais
st.subheader("📈 Indicadores Chave (KPIs)")
col1, col2, col3, col4 = st.columns(4)

total_pedidos = len(df_filtered)
receita_total = df_filtered["Total_Price"].sum()
tempo_medio = df_filtered["Delivery_Duration_Minutes"].mean()
distancia_media = df_filtered["Delivery_Distance_km"].mean()

col1.metric("Total de Pedidos", f"{total_pedidos:,}")
col2.metric("Receita Total", f"R$ {receita_total:,.2f}")
col3.metric("Tempo Médio Entrega", f"{tempo_medio:.1f} min")
col4.metric("Distância Média", f"{distancia_media:.2f} km")

st.markdown("---")

# Gráficos de Primeira Linha
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("🏙️ Volume de Pedidos por Cidade")
    city_counts = df_filtered["City"].value_counts().reset_index()
    city_counts.columns = ["Cidade", "Pedidos"]
    fig_city = px.bar(
        city_counts,
        x="Cidade",
        y="Pedidos",
        color="Pedidos",
        color_continuous_scale="Blues",
        text_auto='.2s'
    )
    st.plotly_chart(fig_city, use_container_width=True)

with row1_col2:
    st.subheader("💳 Métodos de Pagamento")
    fig_pay = px.pie(
        df_filtered,
        names="Payment_Method",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    st.plotly_chart(fig_pay, use_container_width=True)

# Gráficos de Segunda Linha
st.markdown("---")
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("💰 Receita Total por Cidade")
    rev_city = df_filtered.groupby("City")["Total_Price"].sum().reset_index()
    rev_city.columns = ["Cidade", "Receita"]
    fig_rev = px.bar(
        rev_city.sort_values("Receita", ascending=False),
        x="Cidade",
        y="Receita",
        color="Receita",
        color_continuous_scale="Viridis",
        labels={"Receita": "Receita (R$)"}
    )
    st.plotly_chart(fig_rev, use_container_width=True)

with row2_col2:
    st.subheader("🏆 Top 10 Restaurantes")
    top_rest = (
        df_filtered.groupby("Restaurant_ID")["Total_Price"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig_rest = px.bar(
        top_rest,
        x="Restaurant_ID",
        y="Total_Price",
        labels={"Total_Price": "Receita (R$)", "Restaurant_ID": "ID Restaurante"},
        color="Total_Price",
        color_continuous_scale="Magma",
    )
    st.plotly_chart(fig_rest, use_container_width=True)
