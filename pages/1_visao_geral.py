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

st.sidebar.header("Filtros")
cidades = st.sidebar.multiselect(
    "Selecione as Cidades", options=df["City"].unique(), default=df["City"].unique()
)
df_filtered = df[df["City"].isin(cidades)]

col1, col2, col3, col4 = st.columns(4)

total_pedidos = len(df_filtered)
receita_total = df_filtered["Total_Price"].sum()
tempo_medio = df_filtered["Delivery_Duration_Minutes"].mean()
ticket_medio = df_filtered["Total_Price"].mean()

col1.metric("Total de Pedidos", f"{total_pedidos:,}")
col2.metric("Receita Total", f"R$ {receita_total:,.2f}")
col3.metric("Tempo Médio Entrega", f"{tempo_medio:.1f} min")
col4.metric("Ticket Médio", f"R$ {ticket_medio:.2f}")

st.markdown("---")

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Volume de Pedidos por Cidade")
    fig_city = px.bar(
        df_filtered["City"].value_counts().reset_index(),
        x="City",
        y="count",
        labels={"count": "Pedidos", "City": "Cidade"},
        color_discrete_sequence=["#7209b7"],
    )
    st.plotly_chart(fig_city, use_container_width=True)

with row1_col2:
    st.subheader("Distribuição por Método de Pagamento")
    fig_pay = px.pie(
        df_filtered,
        names="Payment_Method",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    st.plotly_chart(fig_pay, use_container_width=True)

st.subheader("Top 10 Restaurantes por Receita")
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
    color_continuous_scale="Viridis",
)
st.plotly_chart(fig_rest, use_container_width=True)
