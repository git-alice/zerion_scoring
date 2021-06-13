import dash
import datetime
import pandas as pd
import pathlib
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
from scipy.interpolate import interp1d
import numpy as np

from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from core.preprocess import preprocess_transactions, preprocess_transaction
from core.parsing import charts_parsing, transactions_parsing, wallet_price_by_timestamps
from core.feature_gen import gen_features

app = dash.Dash(
    __name__,
    external_stylesheets=[
        # './assets/style.css',
        # './assets/app.css'
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

DATA_PATH = pathlib.Path(__file__).parent.joinpath("data").resolve()

# read from datasheet
df = pd.DataFrame()

STARTING_DRUG = ""
DRUG_DESCRIPTION = ''
DRUG_IMG = ''


app.layout = html.Div(
    [
        html.Div(
            [html.Img(src='https://sun9-71.userapi.com/impg/ISXAGmUwVOJKEmK83n7P1z718mUqTjQU5MPXBw/gSpGszCdX7w.jpg?size=357x123&quality=96&sign=b2cf3834b9e50c1d55ee23d1c88c18d6&type=album')], className="app__banner"
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Address scroing",
                                    className="uppercase title",
                                ),
                                html.Span("Enter ", className="uppercase bold"),
                                html.Span(
                                    "the wallet address for scoring"
                                ),
                            ]
                        )
                    ],
                    className="app__header",
                ),
                html.Div(
                    [
                        dcc.Input(
                            id="input",
                            value='0xf58ab01519e5573000cfcb5dc2da4649a5754df5',
                            style={
                                'width': '600px'
                            }
                        )
                    ],
                    className="app__input",
                    style={
                        'display': 'flex',
                        'justify-content': 'center'
                    }
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(
                                    id="graph",
                                    figure={},
                                ),
                            ],
                            # className="two-thirds column",
                            style={
                                'width': '700px !important'
                            }
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H4(
                                            'Score: calculating...',
                                            id="score",
                                            style={
                                                'display': 'block'
                                            }
                                        ),
                                    ],
                                    className="chem__img__container",
                                ),
                                html.Div(
                                    [
                                        html.A(
                                            STARTING_DRUG,
                                            id="chem_name",
                                            href="https://www.drugbank.ca/drugs/DB01002",
                                            target="_blank",
                                        ),
                                        html.P(DRUG_DESCRIPTION, id="chem_desc"),
                                    ],
                                    className="chem__desc__container",
                                ),
                            ],
                            # className="one-third column",
                            style={
                                'width': '200px !important'
                            }
                        ),
                    ],
                    className="container app__content bg-white",
                    style={
                        'width': '1000px !important'
                    }
                ),
                html.Div(
                    [
                        html.Table(
                            {},
                            id="table-element",
                            className="table__container",
                        )
                    ],
                    className="container bg-white p-0",
                ),
            ],
            className="app__container",
        ),
    ]
)


@app.callback(
    [Output("graph", "figure"),
     Output("score", "children")],
    [Input("input", "value")],
)
def update(address):
    """
    Selected chemical dropdown values handler.

    :params chem_dropdown_values: selected dropdown values
    :params plot_type: selected plot graph
    """
    transactions = transactions_parsing(address, setting_path='settings.yaml')
    chunks = preprocess_transactions(transactions)
    df = pd.concat(chunks)
    balances = wallet_price_by_timestamps(address, df['timestamp'], setting_path='settings.yaml')
    df['balance'] = balances
    df['datetime'] = df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))

    scatter = go.Scatter(
        y=df['balance'],
        x=df['datetime'],
        mode='lines+markers',
        line=dict(color='firebrick', width=1),
        marker = dict(color='firebrick', size=6)
    )

    intr = interp1d(df['timestamp'].drop_duplicates().values, df.loc[df['timestamp'].drop_duplicates().index, 'balance'].values, kind='cubic', bounds_error=False)
    intr_x = np.linspace(df['timestamp'].min(), df['timestamp'].max(), 500)

    scatter2 = go.Scatter(
        y=intr(intr_x),
        x=[datetime.datetime.fromtimestamp(x) for x in intr_x.astype(int)],
        mode='lines+markers',
        line=dict(color='green', width=1, dash='dot'),
        marker = dict(color='blue', size=2)
    )

    fig = go.Figure(data=[scatter, scatter2])

    df.index.name = 'transaction'
    df['address'] = address
    df['address_type'] = '???'
    df = df.reset_index().set_index(['address', 'transaction'])
    features = gen_features(df)

    score = 1
    return fig, f'Score: {score}'


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=9000)