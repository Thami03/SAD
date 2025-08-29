import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------
# Configuração da página
# -----------------------------
st.set_page_config(page_title="Dashboard da Lanchonete", layout="wide")

# -----------------------------
# Carregar dados
# -----------------------------
file_path = "Dashboard lula 2.xlsx"
df = pd.read_excel(file_path, sheet_name="Página3")
df["Data"] = pd.to_datetime(df["Data"])
df = df.dropna(subset=["Data"])
df["Origem"] = df["Origem"].fillna("Nulo")
df["Origem"] = df["Origem"].replace("PDV", "Ponto de Venda")

# Ticket médio por dia
ticket_por_dia = df.groupby('Data').agg(
    total=('Valor total', 'sum'),
    pedidos=('Número do Pedido', 'count')
).reset_index()
ticket_por_dia['ticket_medio'] = ticket_por_dia['total'] / ticket_por_dia['pedidos']

# Ticket médio por origem
ticket_por_origem = df.groupby('Origem').agg(
    total=('Valor total', 'sum'),
    pedidos=('Número do Pedido', 'count')
).reset_index()
ticket_por_origem['ticket_medio'] = ticket_por_origem['total'] / ticket_por_origem['pedidos']

# -----------------------------
# Função auxiliar para períodos
# -----------------------------
def gerar_periodo(df, periodo):
    if periodo == "Dia":
        return df["Data"].dt.date
    elif periodo == "Mês":
        return df["Data"].dt.to_period("M").astype(str)
    elif periodo == "Trimestre":
        return df["Data"].dt.to_period("Q").astype(str)
    elif periodo == "Semestre":
        return df["Data"].dt.year.astype(str) + "-S" + ((df["Data"].dt.month - 1)//6 + 1).astype(str)
    return df["Data"].dt.date

# -----------------------------
# Layout
# -----------------------------
st.title(" Dashboard da Lanchonete")

# KPIs principais
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Faturamento Total", f"R$ {df['Valor total'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
with col2:
    st.metric(" Total de Pedidos", f"{df['Número do Pedido'].nunique():,}".replace(",", "."))
with col3:
    st.metric(" Ticket Médio", f"R$ {df['Valor total'].sum()/df['Número do Pedido'].count():.2f}".replace(".", ","))

st.markdown("---")

# -----------------------------
# Origem dos pedidos + Condição de pagamento
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader(" Origem dos Pedidos")
    fig_origem = px.pie(df, names="Origem")
    st.plotly_chart(fig_origem, use_container_width=True)

with col2:
    st.subheader(" Condição de Pagamento")
    fig_pagamento = px.bar(
        df.groupby("Condição de pagamento").size().reset_index(name="Quantidade"),
        x="Condição de pagamento", y="Quantidade",
    )
    st.plotly_chart(fig_pagamento, use_container_width=True)

# -----------------------------
# Evolução das vendas + Retirada
# -----------------------------
st.markdown("## Evolução de Vendas e Retirada")

col1, col2 = st.columns(2)

with col1:
    periodo_vendas = st.selectbox("Período para Vendas", ["Dia", "Mês", "Trimestre", "Semestre"], index=1)
    df_temp = df.copy()
    df_temp["Periodo"] = gerar_periodo(df_temp, periodo_vendas)
    df_grouped = df_temp.groupby("Periodo")["Valor total"].sum().reset_index()
    fig_vendas = px.line(df_grouped, x="Periodo", y="Valor total", title="Evolução de Vendas")
    st.plotly_chart(fig_vendas, use_container_width=True)

with col2:
    periodo_retirada = st.selectbox("Período para Retirada", ["Dia", "Mês", "Trimestre", "Semestre"], index=1)
    df_temp = df.copy()
    df_temp["Periodo"] = gerar_periodo(df_temp, periodo_retirada)
    df_grouped = df_temp.groupby(["Retirada", "Periodo"])["Valor total"].sum().reset_index()
    fig_retirada = px.bar(df_grouped, x="Periodo", y="Valor total", color="Retirada", barmode="stack", title="Retirada x Valor Total")
    st.plotly_chart(fig_retirada, use_container_width=True)

# -----------------------------
# Ticket Médio
# -----------------------------
st.markdown("## Ticket Médio")

periodo_ticket = st.selectbox("Período para Ticket Médio", ["Dia", "Mês", "Trimestre", "Semestre"], index=1)
df_temp = df.copy()
df_temp["Periodo"] = gerar_periodo(df_temp, periodo_ticket)
df_grouped = df_temp.groupby("Periodo").agg(
    total=('Valor total', 'sum'),
    pedidos=('Número do Pedido', 'count')
).reset_index()
df_grouped['ticket_medio'] = df_grouped['total'] / df_grouped['pedidos']
fig_ticket = px.bar(df_grouped, x="Periodo", y="ticket_medio", title="Ticket Médio por Período")
st.plotly_chart(fig_ticket, use_container_width=True)
