from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table
from dash.dependencies import Output, Input, State
import plotly.express as px

# Chargement des données
korian = pd.read_csv("/Users/etienne/Documents/Déploiement/Dash/2207-dash/Evenements_Medicaux_Korian.csv")
format = '%Y/%m/%d %H:%M:%S.%f'
korian['TIME_EVENEMENT'] = pd.to_datetime(korian['DATE_EVENEMENT'], errors='coerce', format=format)
korian['YEAR_EVENEMENT'] = pd.DatetimeIndex(korian['TIME_EVENEMENT']).year
korian = korian[(korian['YEAR_EVENEMENT'] >= 2000) & (korian['YEAR_EVENEMENT'] <= 2021)]

# Initialisation de l'application
app = JupyterDash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Layout de l'application
app.layout = html.Div(children=[
    html.H1('Données médicales Korian'),
    html.Br(),
    
    dbc.Row([
        dbc.Col([
            dcc.Slider(
                id='year_slider',
                min=2010,
                max=2019,
                step=1,
                dots=True,
                included=False,
                marks={k: str(k) for k in range(2010, 2020)},
                value=2010
            ),
        ]),
        dbc.Col([
            dcc.Dropdown(
                id='etab_dropdown',
                options=[{'label': f'Établissement {k}', 'value': f'Etab {k}'} for k in range(1, 16)],
                value='Etab 1'
            )
        ]),
        dbc.Col([
            html.Button(id='submit-button-state', n_clicks=0, children='Submit')
        ]),
    ]),
    dash_table.DataTable(
        id='med_table',
        style_data={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'},
        style_header={'backgroundColor': 'rgb(50, 50, 50)', 'border': '1px solid black'},
        style_cell={'border': '1px solid grey'}
    ),
    dcc.Graph(id='pie_chart')
])

# Callback pour mettre à jour les données et le graphique
@app.callback(
    [Output('med_table', 'data'),
     Output('pie_chart', 'figure')],
    [Input('submit-button-state', 'n_clicks')],
    [State("etab_dropdown", "value"),
     State("year_slider", 'value')]
)
def filter_df(n_clicks, etab, year):
    if n_clicks is None or etab is None or year is None:
        raise PreventUpdate
    else:
        df = korian[korian['YEAR_EVENEMENT'] == year]
        df = df[df['NOM_ETABLISSEMENT'] == etab]
        df = df[['SOURCE', 'NOM_ETABLISSEMENT', 'CODE_EVENEMENT', 'DATE_EVENEMENT']]
        
        fig = px.pie(
            df,
            names='CODE_EVENEMENT',
            title=f"Répartition des tâches dans l'établissement {etab}",
            color_discrete_sequence=px.colors.qualitative.Pastel1
        )
        fig.update_traces(textposition='inside', textinfo='label+percent')
        fig.update_layout(template="plotly_dark")
        
        return df.head(5).to_dict('records'), fig

# Lancement du serveur
app.run_server(mode='inline', port=8049, height=750)
