import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_mantine_components as dmc
import plotly.express as px

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
# Criar gráficos
# -----------------------------
# 1. Origem dos pedidos
fig_origem = px.pie(df, names="Origem")

# 2. Condição de pagamento
fig_pagamento = px.bar(
    df.groupby("Condição de pagamento").size().reset_index(name="Quantidade"),
    x="Condição de pagamento", y="Quantidade",
)

# 3. Evolução diária de vendas
fig_vendas = px.line(
    df.groupby("Data")["Valor total"].sum().reset_index(),
    x="Data", y="Valor total"
)

# 4. Retirada x Valor total
fig_retirada = px.bar(
    df.groupby(["Retirada", "Data"])["Valor total"].sum().reset_index(),
    x="Data", y="Valor total", color="Retirada",
    barmode="stack"
)

# 5. Ticket médio por dia
fig_ticket_dia = px.bar(
    ticket_por_dia, x="Data", y="ticket_medio",
    title="Ticket Médio por Dia"
)

# -----------------------------
# Layout do Dashboard
# -----------------------------
app = Dash(__name__)

app.layout = dmc.MantineProvider(
    children=dmc.Container(
        [
            dmc.Title("📊 Dashboard da Lanchonete", order=1, ta="center", my=20),

            dmc.SimpleGrid(
                cols=2,
                spacing="lg",
                children=[
                    html.Div([
                        dmc.Group(
                            [
                                dmc.Text("Origem dos Pedidos", fw=700, size="lg"),
                                dmc.Tooltip(
                                    label="O gráfico mostra a distribuição dos pedidos conforme sua origem, permitindo identificar de onde vêm as vendas.",
                                    position="right",
                                    withArrow=True,
                                    children=dmc.ActionIcon(
                                        "ℹ️",
                                        variant="light",
                                        color="blue",
                                        size="md",
                                        style={"cursor": "pointer"}
                                    )
                                ),
                            ],
                            gap="xs",  # Corrigido aqui
                            align="center",
                            style={"margin-bottom": "0.5rem"}
                        ),
                        dcc.Graph(figure=fig_origem, style={"height": "400px"})
                    ],
                    style={
                        "border": "2px solid black",
                        "borderRadius": "12px",
                        "padding": "16px",
                        "background": "white"
                    }
                    ),
                    html.Div([
                        dmc.Group(
                            [
                                dmc.Text("Condição de Pagamento", fw=700, size="lg"),
                                dmc.Tooltip(
                                    label="O gráfico mostra a quantidade de pedidos por condição de pagamento, permitindo analisar quais formas de pagamento são mais utilizadas pelos clientes.",
                                    position="right",
                                    withArrow=True,
                                    children=dmc.ActionIcon(
                                        "ℹ️",
                                        variant="light",
                                        color="blue",
                                        size="md",
                                        style={"cursor": "pointer"}
                                    )
                                ),
                            ],
                            gap="xs",
                            align="center",
                            style={"margin-bottom": "0.5rem"}
                        ),
                        dcc.Graph(figure=fig_pagamento, style={"height": "400px"})
                    ],
                    style={
                        "border": "2px solid black",
                        "borderRadius": "12px",
                        "padding": "16px",
                        "background": "white"
                    }
                    ),
                ]
            ),

            dmc.Space(h=30),

            dmc.SimpleGrid(
                cols=2,
                spacing="lg",
                children=[
                    html.Div([
                        dmc.Group(
                            [
                                dmc.Text("Evolução de Vendas por Período", fw=700, size="lg"),
                                dmc.Tooltip(
                                    label="O gráfico mostra a soma dos valores de vendas agrupados pelo período selecionado, permitindo acompanhar a evolução do faturamento ao longo do tempo.",
                                    position="right",
                                    withArrow=True,
                                    children=dmc.ActionIcon(
                                        "ℹ️",
                                        variant="light",
                                        color="blue",
                                        size="md",
                                        style={"cursor": "pointer"}
                                    )
                                ),
                            ],
                            gap="xs",
                            align="center",
                            style={"margin-bottom": "0.5rem"}
                        ),
                        dcc.Dropdown(
                            id="periodo-vendas-dropdown",
                            options=[
                                {"label": "Dia", "value": "D"},
                                {"label": "Mês", "value": "M"},
                                {"label": "Trimestre", "value": "Q"},
                                {"label": "Semestre", "value": "2Q"},
                            ],
                            value="M",
                            clearable=False,
                            style={"margin-bottom": "10px"}
                        ),
                        dcc.Graph(id="fig-vendas-dinamico", style={"height": "400px"})
                    ],
                        style={
                        "border": "2px solid black",
                        "borderRadius": "12px",
                        "padding": "16px",
                        "background": "white"
                    }
                    ),
                    html.Div([
                        dmc.Group(
                            [
                                dmc.Text("Retirada x Valor Total (Delivery x Estabelecimento)", fw=700, size="lg"),
                                dmc.Tooltip(
                                    label="O gráfico mostra o valor total das vendas agrupado por tipo de retirada (delivery, consumido ou retirado no estabelecimento) e pelo período selecionado, permitindo analisar o desempenho de cada canal ao longo do tempo.",
                                    position="right",
                                    withArrow=True,
                                    children=dmc.ActionIcon(
                                        "ℹ️",
                                        variant="light",
                                        color="blue",
                                        size="md",
                                        style={"cursor": "pointer"}
                                    )
                                ),
                            ],
                            gap="xs",
                            align="center",
                            style={"margin-bottom": "0.5rem"}
                        ),
                        dcc.Dropdown(
                            id="periodo-dropdown",
                            options=[
                                {"label": "Dia", "value": "D"},
                                {"label": "Mês", "value": "M"},
                                {"label": "Trimestre", "value": "Q"},
                                {"label": "Semestre", "value": "2Q"},
                            ],
                            value="M",
                            clearable=False,
                            style={"margin-bottom": "10px"}
                        ),
                        dcc.Graph(id="fig-retirada-dinamico", style={"height": "400px"})
                    ],
                    style={
                        "border": "2px solid black",
                        "borderRadius": "12px",
                        "padding": "16px",
                        "background": "white"
                    }
                    )
                ]
            ),

            dmc.Space(h=30),

            html.Div([
                dmc.Group(
                    [
                        dmc.Text("Ticket Médio por Período", fw=700, size="lg"),
                        dmc.Tooltip(
                            label="O gráfico mostra o ticket médio das vendas agrupado pelo período selecionado, permitindo analisar a média de valor gasto por pedido ao longo do tempo.",
                            position="right",
                            withArrow=True,
                            children=dmc.ActionIcon(
                                "ℹ️",
                                variant="light",
                                color="blue",
                                size="md",
                                style={"cursor": "pointer"}
                            )
                        ),
                    ],
                    gap="xs",
                    align="center",
                    style={"margin-bottom": "0.5rem"}
                ),
                dcc.Dropdown(
                    id="periodo-ticket-dropdown",
                    options=[
                        {"label": "Dia", "value": "D"},
                        {"label": "Mês", "value": "M"},
                        {"label": "Trimestre", "value": "Q"},
                        {"label": "Semestre", "value": "2Q"},
                    ],
                    value="M",
                    clearable=False,
                    style={"margin-bottom": "10px", "width": "300px"}
                ),
                dcc.Graph(id="fig-ticket-dinamico", style={"height": "400px"})
            ],
                style={
                    "border": "2px solid black",
                    "borderRadius": "12px",
                    "padding": "16px",
                    "background": "white"
                }
            ),

            dmc.Space(h=50),
        ],
        fluid=True
    )
)

@app.callback(
    Output("fig-ticket-dinamico", "figure"),
    Input("periodo-ticket-dropdown", "value")
)
def atualizar_grafico_ticket(periodo):
    df_temp = df.copy()
    if periodo == "D":
        df_temp["Periodo"] = df_temp["Data"].dt.date
    elif periodo == "M":
        df_temp["Periodo"] = df_temp["Data"].dt.to_period("M").astype(str)
    elif periodo == "Q":
        df_temp["Periodo"] = df_temp["Data"].dt.to_period("Q").astype(str)
    elif periodo == "2Q":
        df_temp["Periodo"] = df_temp["Data"].dt.year.astype(str) + "-S" + ((df_temp["Data"].dt.month - 1)//6 + 1).astype(str)
    else:
        df_temp["Periodo"] = df_temp["Data"].dt.date

    df_grouped = df_temp.groupby("Periodo").agg(
        total=('Valor total', 'sum'),
        pedidos=('Número do Pedido', 'count')
    ).reset_index()
    df_grouped['ticket_medio'] = df_grouped['total'] / df_grouped['pedidos']

    fig = px.bar(
        df_grouped, x="Periodo", y="ticket_medio",
    )
    return fig

@app.callback(
    Output("fig-vendas-dinamico", "figure"),
    Input("periodo-vendas-dropdown", "value")
)
def atualizar_grafico_vendas(periodo):
    df_temp = df.copy()
    if periodo == "D":
        df_temp["Periodo"] = df_temp["Data"].dt.date
    elif periodo == "M":
        df_temp["Periodo"] = df_temp["Data"].dt.to_period("M").astype(str)
    elif periodo == "Q":
        df_temp["Periodo"] = df_temp["Data"].dt.to_period("Q").astype(str)
    elif periodo == "2Q":
        df_temp["Periodo"] = df_temp["Data"].dt.year.astype(str) + "-S" + ((df_temp["Data"].dt.month - 1)//6 + 1).astype(str)
    else:
        df_temp["Periodo"] = df_temp["Data"].dt.date

    df_grouped = df_temp.groupby("Periodo")["Valor total"].sum().reset_index()
    fig = px.line(
        df_grouped,
        x="Periodo", y="Valor total",
    )
    return fig

@app.callback(
    Output("fig-retirada-dinamico", "figure"),
    Input("periodo-dropdown", "value")
)
def atualizar_grafico_retirada(periodo):
    df_temp = df.copy()
    if periodo == "D":
        df_temp["Periodo"] = df_temp["Data"].dt.date
    elif periodo == "M":
        df_temp["Periodo"] = df_temp["Data"].dt.to_period("M").astype(str)
    elif periodo == "Q":
        df_temp["Periodo"] = df_temp["Data"].dt.to_period("Q").astype(str)
    elif periodo == "2Q":
        df_temp["Periodo"] = df_temp["Data"].dt.year.astype(str) + "-S" + ((df_temp["Data"].dt.month - 1)//6 + 1).astype(str)
    else:
        df_temp["Periodo"] = df_temp["Data"].dt.date

    df_grouped = df_temp.groupby(["Retirada", "Periodo"])["Valor total"].sum().reset_index()
    fig = px.bar(
        df_grouped,
        x="Periodo", y="Valor total", color="Retirada",
        barmode="stack"
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)
