import streamlit as st
import pandas as pd
import sqlite3

def load_tables():
    conn = sqlite3.connect("logisfast.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall() if t[0] != 'sqlite_sequence']
    conn.close()
    return tables

def get_table_data(table_name):
    conn = sqlite3.connect("logisfast.db")
    df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 1000", conn)
    conn.close()
    return df

st.title("📋 Consulta de Dados Brutos")

tabelas = load_tables()
tabela_selecionada = st.selectbox("Selecione a Tabela para Visualizar", tabelas)

if tabela_selecionada:
    st.subheader(f"Tabela: {tabela_selecionada}")
    df = get_table_data(tabela_selecionada)
    
    # Busca simples
    busca = st.text_input("Filtrar registros (busca simples no dataframe)")
    if busca:
        df = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)]
    
    st.dataframe(df, use_container_width=True)
    
    st.download_button(
        label="Baixar como CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"{tabela_selecionada}.csv",
        mime="text/csv"
    )
