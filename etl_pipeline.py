import os
import sqlite3

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def run_etl():
    print("🚀 Iniciando Pipeline ETL...")

    CAMINHO_CSV = "talabat_tratado.csv"
    NOME_BANCO = "logisfast.db"

    if not os.path.exists(CAMINHO_CSV):
        print(f"❌ Erro: Arquivo {CAMINHO_CSV} não encontrado.")
        return

    df = pd.read_csv(CAMINHO_CSV)
    print(f"✅ CSV carregado: {len(df):,} linhas.")

    if os.path.exists(NOME_BANCO):
        os.remove(NOME_BANCO)

    conn = sqlite3.connect(NOME_BANCO)
    cursor = conn.cursor()

    cursor.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS CLIENTES (
            User_ID         TEXT PRIMARY KEY,
            City            TEXT,
            Payment_Method  TEXT
        );

        CREATE TABLE IF NOT EXISTS RESTAURANTES (
            Restaurant_ID   INTEGER PRIMARY KEY,
            City            TEXT,
            Restaurant_Lat  REAL,
            Restaurant_Lon  REAL
        );

        CREATE TABLE IF NOT EXISTS ENTREGADORES (
            Driver_ID            INTEGER PRIMARY KEY,
            Driver_Vehicle       TEXT,
            Driver_Availability  TEXT
        );

        CREATE TABLE IF NOT EXISTS PEDIDOS (
            Order_ID                   INTEGER PRIMARY KEY,
            User_ID                    TEXT    REFERENCES CLIENTES(User_ID),
            Restaurant_ID              INTEGER REFERENCES RESTAURANTES(Restaurant_ID),
            Driver_ID                  INTEGER REFERENCES ENTREGADORES(Driver_ID),
            Item_Name                  TEXT,
            Quantity                   INTEGER,
            Total_Price                REAL,
            Order_Time                 TEXT,
            Delivery_Duration_Minutes  INTEGER,
            Order_Status               TEXT,
            Delivery_Distance_km       REAL,
            Coupon_Used                TEXT
        );
    """)

    clientes = (
        df.groupby("User_ID")
        .agg(
            City=("City", lambda x: x.mode()[0]),
            Payment_Method=("Payment_Method", lambda x: x.mode()[0]),
        )
        .reset_index()
    )
    clientes.to_sql("CLIENTES", conn, if_exists="append", index=False)

    restaurantes = df[
        ["Restaurant_ID", "City", "Restaurant_Lat", "Restaurant_Lon"]
    ].drop_duplicates(subset="Restaurant_ID")
    restaurantes.to_sql("RESTAURANTES", conn, if_exists="append", index=False)

    entregadores = df[
        ["Driver_ID", "Driver_Vehicle", "Driver_Availability"]
    ].drop_duplicates(subset="Driver_ID")
    entregadores.to_sql("ENTREGADORES", conn, if_exists="append", index=False)

    colunas_pedidos = [
        "Order_ID",
        "User_ID",
        "Restaurant_ID",
        "Driver_ID",
        "Item_Name",
        "Quantity",
        "Total_Price",
        "Order_Time",
        "Delivery_Duration_Minutes",
        "Order_Status",
        "Delivery_Distance_km",
        "Coupon_Used",
    ]
    df[colunas_pedidos].to_sql("PEDIDOS", conn, if_exists="append", index=False)

    print("✅ Banco de dados populado.")

    query_sql = """
        SELECT
            C.User_ID,
            C.City,
            C.Payment_Method,
            COUNT(P.Order_ID)                                  AS frequencia,
            ROUND(AVG(P.Total_Price), 2)                       AS ticket_medio,
            ROUND(AVG(P.Delivery_Duration_Minutes), 1)         AS tempo_entrega_medio,
            ROUND(100.0 * SUM(CASE WHEN P.Coupon_Used = 'Yes' THEN 1 ELSE 0 END)
                  / COUNT(P.Order_ID), 1)                      AS taxa_uso_cupom
        FROM PEDIDOS P
        JOIN CLIENTES C ON P.User_ID = C.User_ID
        WHERE P.Order_Status = 'Delivered'
        GROUP BY C.User_ID, C.City, C.Payment_Method
    """
    df_extraido = pd.read_sql_query(query_sql, conn)

    features = ["frequencia", "ticket_medio", "tempo_entrega_medio", "taxa_uso_cupom"]
    X = df_extraido[features].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df_extraido["Cluster"] = kmeans.fit_predict(X_scaled)

    pca = PCA(n_components=2, random_state=42)
    pca_results = pca.fit_transform(X_scaled)
    df_extraido["PCA1"] = pca_results[:, 0]
    df_extraido["PCA2"] = pca_results[:, 1]

    df_extraido.to_sql("CLIENTES_SEGMENTADOS", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()
    print("✅ Segmentação concluída e salva na tabela 'CLIENTES_SEGMENTADOS'.")
    print("🏁 Pipeline finalizado com sucesso.")


if __name__ == "__main__":
    run_etl()
