from dash import Dash, Input, Output, html, dcc
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta, date

# Suponha que você tenha seus dados carregados em um DataFrame 'df'

app = Dash(__name__)

# Layout da aplicação
app.layout = html.Div(children=[
    html.H1(children='Receita X Despesa', style={'margin-bottom': '1rem'}),

    html.Div([
        html.Div([
            html.Div([
                dcc.DatePickerRange(
                    id="date-range-picker",
                    min_date_allowed=date(2020, 8, 5),
                    initial_visible_month=datetime.now().date(),
                    start_date=datetime.now().date(),
                    end_date=datetime.now().date() + timedelta(days=5),
                    style={"width": "330px"},
                ),
                html.Div(id="selected-date-date-range-picker", style={"margin-top": "10px"}),
            ])
        ], className="col"),
        html.Div([
            html.H3(children='Selecione a Provisão'),
            html.Div([
                dcc.Checklist(
                    options=[
                        {'label': 'Provisão', 'value': 'Provisão'},
                        {'label': 'Real', 'value': 'Real'}
                    ],
                    className="mb-3",
                    id="provisao-real"
                )
            ])
        ], className="col"),
        html.Div([
            html.Div([
                html.H4("Total de Receitas"),
                html.P(id="total-receitas", className="p-3 fs-3")
            ], className='card mb-2 rounded-3', style={'color': 'white', 'background': '#101726'})
        ], className='col text-center'),
        html.Div([
            html.Div([
                html.H4("Total de Despesas"),
                html.P(id="total-despesas", className="p-3 fs-3")
            ], className='card mb-2 rounded-3', style={'color': 'white', 'background': '#E74827'})
        ], className="col text-center")
    ], className="row align-items-center"),

    dcc.Graph(
        id='bar-chart'
    )
], className="container text-center")

# Callback para atualizar os totais de receitas e despesas
@app.callback(
    Output('total-receitas', 'children'),
    Output('total-despesas', 'children'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date')
)
def update_totals(start_date, end_date):
    # Aqui você pode calcular os totais de receitas e despesas com base nas datas selecionadas
    soma_receitas = df[(df['data'] >= start_date) & (df['data'] <= end_date) & (df['tipo'] == 'RECEITAS')]['vlr'].sum()
    soma_despesas = df[(df['data'] >= start_date) & (df['data'] <= end_date) & (df['tipo'] == 'DESPESAS')]['vlr'].sum()

    return f"R$ {round(soma_receitas, 2)}", f"R$ {round(soma_despesas, 2)}"


# Callback para atualizar o gráfico
@app.callback(
    Output('bar-chart', 'figure'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('provisao-real', 'value')
)
def update_chart(start_date, end_date, provisao_real):
    filtered_df = df.copy()

    filtered_df = filtered_df[
        (filtered_df['data'] >= start_date) & (filtered_df['data'] <= end_date)
    ]

    if provisao_real:
        filtered_df = filtered_df[filtered_df['provisao'].isin(provisao_real)]

    fig = px.bar(filtered_df, x='codemp', y='vlr', color='tipo', barmode='group',
                 labels=dict(codemp='Empresa', vlr='Valor', tipo='Tipo'),
                 title='Receita e Despesa por Empresa')
    fig.update_traces(textposition='outside')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
