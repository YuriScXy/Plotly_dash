from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


import pandas as pd
import connexao as conn
from datetime import datetime, timedelta, date
import locale

import dash_mantine_components as dmc
from dash import Input, Output, html, callback
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/dayjs.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/locale/br.min.js",]
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

app = Dash(__name__,external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = conn.consulta()


dados_agrupados = df.groupby(['Empresa', 'tipo'])['Valor'].sum().reset_index()
dados_agrupados["Valor"] = round(dados_agrupados["Valor"], 2)

soma_receitas = 0
soma_despesas = 0

dict_tradu = df.to_dict(orient='records')

for i in dict_tradu:
    if i["tipo"] == "RECEITAS":
        soma_receitas += i["Valor"]
    else:
        soma_despesas += i["Valor"]


dados_agrupados_receita = dados_agrupados[(dados_agrupados['tipo'] == 'RECEITAS')]
dados_agrupados_despesa = dados_agrupados[(dados_agrupados['tipo'] == 'DESPESA')]

fig = px.bar(dados_agrupados, x='Empresa', y='Valor', color='tipo',
             barmode='group', title='Receita e Despesa por Empresa',
             labels={'Valor': 'Valor Total', 'tipo': 'Tipo'},
             category_orders={"tipo" : ["RECEITAS", "DESPESA"]},
             text="Valor",
             color_discrete_map={'Receitas' : 'rgb(16,23,38)','Despesa' : 'rgb(231,72,39)'})

app.layout = html.Div([
        dmc.Navbar(
                p="md",
                width={"base": 300},
                height=500,
                children=[
                    
                    html.Div([
                        html.Div(
                        [
                            html.H3(
                                children='Selecione a Data'
                            ),
                            dmc.DateRangePicker(
                                id="dataFilter",
                                minDate=date(2020, 8, 5),
                                value=[datetime.now().date() - timedelta(days=5), datetime.now().date()],
                                style={"width": 330},
                            ),
                        ]
                        ),
                    ],className="col"),
                    html.Div([
                        html.H3(
                            children='Selecione a Provisão'
                        ),
                        html.Div([
                            dmc.Switch(
                                size="md",
                                label="Provisão",
                                className="mb-3",
                                id="swt-provisao"
                            ),
                            dmc.Switch(
                                size="md",
                                label="Real",
                                className="mb-3",
                                id="swt-real"
                            )
                        ])
                    ],className="col"),                
                    html.Div([
                        html.H3(
                            children='Selecione a Situação'
                        ),
                        html.Div([
                            dmc.Switch(
                            size="md",
                            label="Pendente",
                            className="mb-3 mt-2",
                            id="swt-pendente"
                            ),
                        ]),
                        html.Div([
                            dmc.Switch(
                            size="md",
                            label="Não Pendente",
                            className="mb-3 mt-2",
                            id="swt-pendente-2"
                            ),
                        ]),
                        
                    ], className="col")
                ],className="col-3 align-items-center"
        ),
        html.Div(children=[
            html.Div([
                html.H1(children='Receita X Despesa',className="mb-3 text-center"),   
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4("Total de Receitas"),
                            html.P(f"R$ {locale.currency(round(soma_receitas,2), grouping=True, symbol=None)}",className="p-3 fs-3",id="somaReceita")
                        ], className='card mb-2 rounded-3 ',style={'color' : 'white', 'background' : '#101726'})
                    ],className='col text-center mx-auto'),
                    html.Div([
                        
                        html.Div([
                            html.H4("Total de Despesas"),
                            html.P(f"R$ {locale.currency(round(soma_despesas,2), grouping=True, symbol=None)}",className="p-3 fs-3",id="somaDespe")
                        ], className='card mb-2 rounded-3 ',style={'color' : 'white', 'background' : '#E74827'}),
                    ],className="col text-center mx-auto")
                        
                ],className="row"),
                
                    dcc.Graph(
                        id='graph_1',
                        
                        figure=fig,    
                    )
            ],className="w-75 mx-auto",style={"width" : 1280})
     ],className="col")
],className="row justify-content-start")

@app.callback(
    Output('graph_1','figure'),
    Output('somaDespe','children'),
    Output('somaReceita','children'),
    Input('dataFilter', 'value'),
    Input('swt-provisao','checked'),
    Input('swt-real','checked'),
    Input('swt-pendente','checked'),
    Input('swt-pendente-2','checked')        
)
def provisaChecked(datas,provisao, real,pendente,nPendente):
    
    
    tabelaFiltrada = df.copy()
    
    tabelaFiltrada = tabelaFiltrada.loc[
        (tabelaFiltrada['data'] >= datetime.strptime(datas[0], '%Y-%m-%d')) &
        (tabelaFiltrada['data'] <= datetime.strptime(datas[1], '%Y-%m-%d'))
    ]
    
    if not provisao and not real:
        pass  # Mantém os dados originais
        
    if provisao and not real:
        tabelaFiltrada = tabelaFiltrada.loc[(tabelaFiltrada['provisao'] == 'Provis?o')]
        print(tabelaFiltrada)
            
    if not provisao and real:
        tabelaFiltrada = tabelaFiltrada.loc[(tabelaFiltrada['provisao'] == 'Real')]
    
    if pendente and not nPendente:
        tabelaFiltrada = tabelaFiltrada.loc[(tabelaFiltrada['status'] == 'S')]
        
    if not pendente and nPendente:
        tabelaFiltrada = tabelaFiltrada.loc[(tabelaFiltrada['status'] == 'N')]
        
    if (not pendente and not nPendente) and (pendente and nPendente):
        pass
    
    if tabelaFiltrada.empty:
        empty_fig = px.bar(x=[], y=[], labels=dict(x="Empresa", y="Valor", color="Tipo"), title='Sem dados para exibir')
        return empty_fig
    
        
       
    dict_tradu = tabelaFiltrada.to_dict(orient='records')
    soma_receitas = 0
    soma_despesas = 0
    
    for i in dict_tradu:
        if i["tipo"] == "RECEITAS":
            soma_receitas += i["Valor"]
        else:
            soma_despesas += i["Valor"]
    print(soma_receitas,soma_despesas)
    dados_agrupados_2 = tabelaFiltrada.groupby(['Empresa', 'tipo'])['Valor'].sum().reset_index()
    
    dados_agrupados_2["Valor"] = round(dados_agrupados_2["Valor"], 2)
    
    fig = px.bar(dados_agrupados_2, x='Empresa', y='Valor', color='tipo',
             barmode='group', title='Receita e Despesa por Empresa',
             labels={'Valor': 'Valor Total', 'tipo': 'Tipo'},
             category_orders={"tipo" : ["RECEITAS", "DESPESA"]},
             text="Valor",
             color_discrete_map={'RECEITAS' : 'rgb(16,23,38)','DESPESA' : 'rgb(231,72,39)'})
    fig.update_traces(textposition="outside", cliponaxis=False,)
    return [fig,f"R$ {locale.currency(round(soma_despesas,2), grouping=True, symbol=None)}",f"R$ {locale.currency(round(soma_receitas,2), grouping=True, symbol=None)}"]


if __name__ == '__main__':
    app.run(debug=True)
