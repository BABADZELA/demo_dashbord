from cProfile import label
from distutils.log import debug
from turtle import title

from click import style
import dash
# import dash_core_components as dcc
# import dash_html_components as html
from dash import html
from dash import dcc
import plotly
import plotly.graph_objs as go
from dash.dependencies import Input, Output
# import dash_table
from dash import dash_table
import pandas as pd
from pandas import DataFrame
import numpy as np
import folium
import os

# Import des données
df_auto = pd.read_csv(r'dataset/dataRecuperees/auto.csv', dtype='unicode')
df_salaire = pd.read_csv(r'dataset/dataRecuperees/salaires.csv', dtype='unicode')
df_emploi = pd.read_csv(r'dataset/dataRecuperees/emploi.csv', dtype='unicode')
df_immobilier = pd.read_csv(r'dataset/dataRecuperees/immobilier.csv')
df_entreprises = pd.read_csv(r'dataset/dataRecuperees/entreprises.csv', dtype='unicode')
df_chomage = pd.read_csv(r'dataset/dataRecuperees/chomage.csv')
df_ville = pd.read_csv(r'dataset/dataRecuperees/liensVilles.csv', dtype='unicode')
df_demographie = pd.read_csv(r'dataset/dataRecuperees/demographie.csv', dtype='unicode')
df_infos = pd.read_csv(r'dataset/dataRecuperees/infos.csv', dtype='unicode')

# liste des villes
villes = [{
    'label': ville,
    'value': ville
} for ville in df_ville['ville'].unique()]

app = dash.Dash(__name__)

# layout va contenir toutes les divs de notre application
app.layout = html.Div([
    html.Div([
        html.H4('Choisissez une ville'),
        dcc.Dropdown(
            id = 'ville-picker',
            options = villes,
            value = 'Paris (75000)'
        )
    ], style={
        'width': '25%',
        'border': '1px solid #eee',
        'padding': '30px 30px 30px 120px',
        'box-shadow': '0 2px 2px #CCC',
        'display': 'inline-block',
        'verticalAlign': 'top',
    }),
    html.Div([
        # Tabs permet de générer une barre de navigation, les children sont les titres de chaque onglet
        dcc.Tabs(
            id = 'tabs',
            value = 'tab-1',
            children = [
                # infos générales
                dcc.Tab(label='Infos Générales', children=[
                    html.Div([
                        html.H3('Infos Générales')
                    ], style={'background': 'blue', 'color': 'white', 'text-align': 'center', 'padding': '2px 0 2px 0'}),
                    
                    html.Div([
                        # permet de générer des tableaux
                        dash_table.DataTable(
                            id = 'table_infos',
                            style_cell = {'font-family': 'Montserrat'},
                            style_data_conditional = [ # il s'agit d'une clé pour les conditions sur les lignes propres à dash
                                {
                                    'if' : {'column_id': 'intitule'},
                                    'textAlign': 'left'
                                }
                            ] + [{
                                'if': {'row_index': 'odd'}, # condition pour si les lignes sont impairs
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }],
                            style_header = {
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold',                             
                            }
                        )
                    ], style={'width': '40%', 'border': '1px solid #eee', 'box-shadow': '0 2px #ccc', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '60px 30px 60px 30px'}),
                    
                    html.Div(id = 'map', style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '50%', 'padding': '15px 0 15px 10px'}),
                ]),
                # onglet démographie
                dcc.Tab(label='Démographie', children = [
                    html.H3('Population Française', style={'background': 'blue', 'color': 'white', 'textAlign': 'center', 'padding': '2px 0 2px 0'}),
                    html.Div([
                        dcc.Graph(id='population')
                    ], style={'border': '1px solid #eee', 'box-shadow': '0 2px 2px #ccc', 'display': 'inline-block', 'verticalAlign': 'top',
                    'width': '45%', 'padding': '50px 0 0 50px'}),
                    html.Div([
                        dcc.Graph(id='naissances_deces')
                    ], style={'border': '1px solid #eee', 'box-shadow': '0 2px 2px #ccc', 'display': 'inline-block', 'verticalAlign': 'top',
                    'width': '45%', 'padding': '50px 0 0 50px'}),
                    html.Div([
                        dcc.Graph(id = 'hommes_femmes')
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '35%', 'box-shadow': '0 2px 2px #ccc', 'padding': '4px 0 4px 0'}),
                    html.Div([
                        dcc.Graph(id = 'ages')
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '35%', 'box-shadow': '0 2px 2px #ccc', 'padding': '4px 0 4px 0'}),
                    html.Div([
                        dash_table.DataTable(
                            id ='repartitions',
                            style_cell = {'font-family': 'Montserrat'},
                            style_data_conditional = [ # il s'agit d'une clé pour les conditions sur les lignes propres à dash
                                {
                                    'if' : {'column_id': 'intitule'},
                                    'textAlign': 'left'
                                }
                            ] + [{
                                'if': {'row_index': 'odd'}, # condition pour si les lignes sont impairs rendre les couleurs de lignes grises
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }],
                            style_header = {
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold',
                                'textAlign': 'center',                             
                            }
                        )
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '25%', 'paddingTop': '50px', 'height': '100%', 'box-shadow': '0 2px 2px #ccc'}),
                    
                    html.Div([
                        dcc.Graph(id = 'familles')
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '35%', 'box-shadow': '0 2px 2px #ccc', 'padding': '4px 0 4px 0'}),
                    html.Div([
                        dcc.Graph(id = 'statut_marial')
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '35%', 'box-shadow': '0 2px 2px #ccc', 'padding': '4px 0 4px 0'}),
                    html.Div([
                        dash_table.DataTable(
                            id ='repartitions_2',
                            style_cell = {'font-family': 'Montserrat'},
                            style_data_conditional = [ # il s'agit d'une clé pour les conditions sur les lignes propres à dash
                                {
                                    'if' : {'column_id': 'intitule'},
                                    'textAlign': 'left'
                                }
                            ] + [{
                                'if': {'row_index': 'odd'}, # condition pour si les lignes sont impairs rendre les couleurs de lignes grises
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }],
                            style_header = {
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold',
                                'textAlign': 'center',                             
                            }
                        )
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '25%', 'paddingTop': '50px', 'height': '200px', 'box-shadow': '0 2px 2px #ccc'}),
                    
                    html.H3('Population étrangère', style={'background': 'blue', 'color': 'white', 'textAlign': 'center', 'padding': '2px 0 2px 0'}),
                    html.Div([
                        dcc.Graph(id='evolution_etrangers')
                    ], style={'display': 'block', 'verticalAlign': 'top', 'width': '100%', 'box-shadow': '0 2px 2px #ccc'}),
                    html.Div([
                        dcc.Graph(id='repartition_etrangers_HF')
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '35%', 'box-shadow': '0 2px 2px #ccc', 'padding': '4px 0 4px 0'}),
                    html.Div([
                        dcc.Graph(id='repartion_etrangers_ages')
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '35%', 'box-shadow': '0 2px 2px #ccc', 'padding': '4px 0 4px 0'}),
                    html.Div([
                        dash_table.DataTable(
                            id='tableau_etrangers',
                            style_cell = {'font-family': 'Montserrat'},
                            style_data_conditional = [ # il s'agit d'une clé pour les conditions sur les lignes propres à dash
                                {
                                    'if' : {'column_id': 'intitule'},
                                    'textAlign': 'left'
                                }
                            ] + [{
                                'if': {'row_index': 'odd'}, # condition pour si les lignes sont impairs rendre les couleurs de lignes grises
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }],
                            style_header = {
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold',
                                'textAlign': 'center',                             
                            }
                        )
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '25%', 'paddingTop': '50px', 'height': '409px', 'box-shadow': '0 2px 2px #ccc'}),

                    html.H3('Population immigrée', style={'background': 'blue', 'color': 'white', 'textAlign': 'center', 'padding': '2px 0 2px 0'}),
                    html.Div([
                        dcc.Graph(id='evolution_immigres')
                    ], style={'display': 'block', 'verticalAlign': 'top', 'width': '100%', 'box-shadow': '0 2px 2px #ccc'}),
                    html.Div([
                        dcc.Graph(id='repartition_immigres_HF')
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '35%', 'box-shadow': '0 2px 2px #ccc', 'padding': '4px 0 4px 0'}),
                    html.Div([
                        dcc.Graph(id='repartion_immigres_ages')
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '35%', 'box-shadow': '0 2px 2px #ccc', 'padding': '4px 0 4px 0'}),
                    html.Div([
                        dash_table.DataTable(
                            id='tableau_immigres',
                            style_cell = {'font-family': 'Montserrat'},
                            style_data_conditional = [ # il s'agit d'une clé pour les conditions sur les lignes propres à dash
                                {
                                    'if' : {'column_id': 'intitule'},
                                    'textAlign': 'left'
                                }
                            ] + [{
                                'if': {'row_index': 'odd'}, # condition pour si les lignes sont impairs rendre les couleurs de lignes grises
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }],
                            style_header = {
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold',
                                'textAlign': 'center',                             
                            }
                        )
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '25%', 'paddingTop': '50px', 'height': '409px', 'box-shadow': '0 2px 2px #ccc'}),
                ]),
                # onglet Emploi
                dcc.Tab(label='Emploi', children = [
                    html.Div([
                        html.H2('Emploi / Chomage')
                    ], style={'background': 'blue', 'color': 'white', 'textAlign': 'center', 'padding': '1px 0px'}),
                    html.Div([
                        dcc.Graph(id='evolution_chomage')
                    ]),
                    html.Div([
                        dcc.Graph(id='emploi_HF')
                    ], style={'width': '45%', 'display': 'inline-block', 'paddingLeft': '30px'}),
                    html.Div([
                        dash_table.DataTable(
                            id='table_emploi_HF',
                            style_cell = {'font-family': 'Montserrat'},
                            style_data_conditional = [ # il s'agit d'une clé pour les conditions sur les lignes propres à dash
                                {
                                    'if' : {'column_id': 'intitule'},
                                    'textAlign': 'left'
                                }
                            ] + [{
                                'if': {'row_index': 'odd'}, # condition pour si les lignes sont impairs
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }],
                            style_header = {
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold',                             
                            }
                        )
                    ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '30px 30px 0px 30px'}),

                    html.Div([
                        dcc.Graph(id='emploi_age')
                    ], style={'width': '45%', 'display': 'inline-block', 'paddingLeft': '30px'}),
                    html.Div([
                        dash_table.DataTable(
                            id='table_age',
                            style_cell = {'font-family': 'Montserrat'},
                            style_data_conditional = [ # il s'agit d'une clé pour les conditions sur les lignes propres à dash
                                {
                                    'if' : {'column_id': 'intitule'},
                                    'textAlign': 'left'
                                }
                            ] + [{
                                'if': {'row_index': 'odd'}, # condition pour si les lignes sont impairs
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }],
                            style_header = {
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold',                             
                            }
                        )
                    ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '30px 30px 0px 30px'}),

                ]),
                dcc.Tab(label='Evolution du chomage', children = [
                    html.Div([
                        html.H2(id='annee', style={'textAlign': 'center'})
                    ]),
                    html.Div(id='map_chomage'),
                    html.Div([
                        dcc.Slider(id='slider', 
                            min=2004, 
                            max=2008, 
                            marks={annee : str(annee) for annee in range(2004, 2009)},
                            value=2004,)
                    ], style={})
                ])
            ]
        )
    ])
])


############################################## ONGLETS INFOS GENERAL #############################################################""
# Pour l'ajout des données dans les tables on va rajouter des décorateurs qui sont des fonctions que d'autres fonctions utilisent pour 
# être excécutées

@app.callback([Output('table_infos', 'data'), Output('table_infos', 'columns')], [Input('ville-picker', 'value')])
def update_generales(ville_choisie):
    colonnes = df_infos.columns
    # liste des colonnes à ne récupérer et qui ne seront pas représentées dans notre dashbord
    colonnes_off = ['Taux de chômage (2015)', 'Etablissement public de coopération intercommunale (EPCI)', 'lien', 
    'Unnamed: 0', 'Pavillon bleu', "Ville d'art et d'histoire", 'Ville fleurie', 'Ville internet', 'ville']

    listeInfos = [info for info in colonnes if info not in colonnes_off]

    infos = {
        'intitule': listeInfos,
        'donnee': [df_infos[df_infos['ville'] == ville_choisie][col].iloc[0] for col in listeInfos]
    }

    table = DataFrame(infos)

    # données à retourner ainsi que les en-têtes
    data = table.to_dict('rows')

    entete = {'id': 'intitule', 'name': " "}, {'id': 'donnee', 'name': ville_choisie}

    return data, entete

# Afficher la localisation sur une carte
# output('map', 'chidren') signifie que dans l'objet ayant pour identifiant #map il va retourner une chidren dans laquelle on mettra une Iframe
# Pour le Input, on récupère l'objet dans l'identifiant est ville-picker et on récupère sa valeur=value pour la donner en entrée
@app.callback(Output('map', 'children'), [Input('ville-picker', 'value')])
def update_location(ville_choisie):
    longitude = df_infos[df_infos['ville'] == ville_choisie]['Longitude'].iloc[0]
    latitude = df_infos[df_infos['ville'] == ville_choisie]['Latitude'].iloc[0]

    carte = folium.Map(location=(latitude, longitude), zoom_start=7)
    marker = folium.Marker(location=[latitude, longitude])
    marker.add_to(carte)

    # pour eviter de recharger la carte pour chacune des communes, il a été decidé de stocker les cartes de toutes les communes visitées dans 
    # le dossier location

    fichier = f'location/localisation_{ville_choisie}.html'

    if not os.path.isfile(fichier): # si le fichier n'existe pas 
        carte.save(fichier)

    return html.Iframe(srcDoc = open(fichier, 'r').read(), width='100%', height='600')

############################################## ONGLET DEMOGRAPHIE #######################################################################
@app.callback(Output('population', 'figure'), [Input('ville-picker', 'value')])
def population_graph(ville_choisie):
    x_axis = np.array(range(2006, 2016))
    y_axis = [
        df_demographie[df_demographie['ville'] == ville_choisie]["nbre habitants (" + str(annee) + ")"].iloc[0] for annee in range(2006, 2016)
    ]

    # IMPORTANT!! à redéfinir après avoir récupéré les données
    ville_choisie = ville_choisie.split('(')[0].strip()

    traces_graph = []

    traces_graph.append(
        go.Scatter(
            x = x_axis,
            y = y_axis,
            mode='lines+markers',
            line={'shape': 'spline', 'smoothing': 1}
        )
    )

    return {
        'data': traces_graph,
        'layout': go.Layout(
            title = f'Evolution de la population à {ville_choisie}',
            xaxis = {'title': 'Années'},
            yaxis = dict(title = "Nombre d'habitants"),
            hovermode = 'closest', # permet d'afficher des informations au survole du point
            legend_orientation = 'h' # Ajout de la légende lorsqu'on a plusieurs graph
        )
    }

# Evolution des naissances et decès
@app.callback(Output('naissances_deces', 'figure'), [Input('ville-picker', 'value')])
def naissances_deces_graph(ville_choisie):
    x_axis = np.array(range(1999, 2017))
    y_axis_naissances = [
        df_demographie[df_demographie['ville'] == ville_choisie]["nbre naissances (" + str(annee) + ")"].iloc[0] for annee in range(1999, 2017)
    ]
    y_axis_deces = [
        df_demographie[df_demographie['ville'] == ville_choisie]["nbre deces (" + str(annee) + ")"].iloc[0] for annee in range(1999, 2017)
    ]

    # IMPORTANT!! à redéfinir après avoir récupéré les données
    ville_choisie = ville_choisie.split('(')[0].strip()

    traces_graph = [
        go.Scatter(
            x = x_axis,
            y = y_axis_naissances,
            mode = 'lines+markers',
            line = {'shape': 'spline', 'smoothing': 1},
            name = f'Naissances à {ville_choisie}',
        ),

        go.Scatter(
            x = x_axis,
            y = y_axis_deces,
            mode = 'lines+markers',
            line = {'shape': 'spline', 'smoothing': 1},
            name = f'Naissances à {ville_choisie}',
        ),
    ]

    return {
        'data': traces_graph,
        'layout': go.Layout(
            title = f'Evolution des Naissances et Décès à {ville_choisie}',
            xaxis = {'title': 'Années'},
            yaxis = {'title': 'Nombre de personnes'},
            hovermode = 'closest',
            legend_orientation = 'h',
        )
    }

# Afficher le camembert répartition hommes / femmes
@app.callback(Output('hommes_femmes', 'figure'), [Input('ville-picker', 'value')])
def repartition_HF(ville_choisie):
    nb_hommes = df_demographie[df_demographie['ville'] == ville_choisie]['Hommes'].iloc[0]
    nb_femmes = df_demographie[df_demographie['ville'] == ville_choisie]['Femmes'].iloc[0]

    label = ['Hommes', 'Femmes']
    values = [float(nb_hommes), float(nb_femmes)]
    total = sum(values)

    traces_graph = [
        go.Pie(labels = label, values= values)
    ]

    return {
        'data': traces_graph,
        'layout': go.Layout( # c'est la zone où l'on va afficher notre graph
            title = f'Répartition Hommes/Femmes<br> (Total: {str(total)})',
            legend_orientation = 'h'
        )
    }

# Répartition par tranches d'âge
@app.callback(Output('ages', 'figure'), [Input('ville-picker', 'value')])
def repartition_ages(ville_choisie):
    colonnes = ['Moins de 15 ans', '15 - 29 ans', '30 - 44 ans', '45 - 59 ans', '60 - 74 ans', '75 ans et plus']

    labels = colonnes
    value = [float(df_demographie[df_demographie['ville'] == ville_choisie][item].iloc[0]) for item in colonnes]
    total = sum(value)

    traces_graph = [
        go.Pie(labels = labels, values= value)
    ]

    return {
        'data': traces_graph,
        'layout': go.Layout(
            title = f"Répartition par Tranches d'âges<br> (Total: {str(total)})",
            legend_orientation = 'h'
        )
    }

# tableau des données de la répartition
@app.callback([Output('repartitions', 'data'), Output('repartitions', 'columns')], [Input('ville-picker', 'value')])
def table_repartition(ville_choisie):
    colonnes = ['Hommes', 'Femmes', 'Moins de 15 ans', '15 - 29 ans', '30 - 44 ans', '45 - 59 ans', '60 - 74 ans', '75 ans et plus']

    infos = {
        'intitule': colonnes,
        'donnee': [df_demographie[df_demographie['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes]
    }

    table_donnee = DataFrame(infos)
    data = table_donnee.to_dict('rows')

    entete = [{'id': 'intitule', 'name': 'Intitulé'}, {'id': 'donnee', 'name': ville_choisie.split('(')[0].strip()}]

    return data, entete

# Répartition des familles
@app.callback(Output('familles', 'figure'), [Input('ville-picker', 'value')])
def repartition_famille(ville_choisie):
    colonnes = ['Familles monoparentales', 
'Couples sans enfant', 'Couples avec enfant', 'Familles sans enfant', 'Familles avec un enfant', 
'Familles avec deux enfants', 'Familles avec trois enfants', 'Familles avec quatre enfants ou plus']

    labels = colonnes
    values = [float(df_demographie[df_demographie['ville'] == ville_choisie][colonne].iloc[0]) for colonne in colonnes]

    total = sum(values)

    traces_data = [
        go.Pie(labels = labels, values = values)
    ]

    return {
        'data': traces_data,
        'layout': go.Layout(
            title = f'Composition des familles<br> (Total: {total})',
            legend_orientation = 'h',

        )
    }

# Répartition du statut marital
@app.callback(Output('statut_marial', 'figure'), [Input('ville-picker', 'value')])
def repartition_famille(ville_choisie):
    colonnes = ['Personnes célibataires', 'Personnes mariées', 'Personnes divorcées', 'Personnes veuves']

    labels = colonnes
    values = [float(df_demographie[df_demographie['ville'] == ville_choisie][colonne].iloc[0]) for colonne in colonnes]

    total = sum(values)

    traces_data = [
        go.Pie(labels = labels, values = values)
    ]

    return {
        'data': traces_data,
        'layout': go.Layout(
            title = f'Statut des familles<br> (Total: {total})',
            legend_orientation = 'h',

        )
    }

# tableau 2 des données de la répartition
@app.callback([Output('repartitions_2', 'data'), Output('repartitions_2', 'columns')], [Input('ville-picker', 'value')])
def table_repartition(ville_choisie):
    colonnes = ['Familles monoparentales', 
'Couples sans enfant', 'Couples avec enfant', 'Familles sans enfant', 'Familles avec un enfant', 
'Familles avec deux enfants', 'Familles avec trois enfants', 'Familles avec quatre enfants ou plus',
'Personnes célibataires', 'Personnes mariées', 'Personnes divorcées', 'Personnes veuves']

    infos = {
        'intitule': colonnes,
        'donnee': [df_demographie[df_demographie['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes]
    }

    table_donnee = DataFrame(infos)
    data = table_donnee.to_dict('rows')

    entete = [{'id': 'intitule', 'name': 'Intitulé'}, {'id': 'donnee', 'name': ville_choisie.split('(')[0].strip()}]

    return data, entete

# Evolution des étrangres et des immigrés
@app.callback([Output('evolution_etrangers', 'figure'), Output('evolution_immigres', 'figure')], [Input('ville-picker', 'value')])
def evolution_etrangers_et_immigres(ville_choisie):
    x_axis = np.array(range(2006, 2016))
    y_axis_etrangers = [df_demographie[df_demographie['ville'] == ville_choisie]["nbre étrangers (" + str(annee) + ")"].iloc[0] for annee in range(2006, 2016)]
    y_axis_immigres = [df_demographie[df_demographie['ville'] == ville_choisie]["nbre immigrés (" + str(annee) + ")"].iloc[0] for annee in range(2006, 2016)]

    traces_etrangers = [
        go.Scatter(
            x=x_axis,
            y=y_axis_etrangers,
            line={'shape': 'spline', 'smoothing': 1}
        )
    ]

    traces_immigres = [
        go.Scatter(
            x=x_axis,
            y=y_axis_immigres,
            line={'shape': 'spline', 'smoothing': 1}
        )
    ]

    ville_choisie = ville_choisie.split('(')[0].strip()
    
    figuresEtrangers = {
        'data': traces_etrangers,
        'layout': go.Layout(
            title = f'Evolution de la population etrangère<br> à {ville_choisie}',
            xaxis = {'title': 'Années'},
            yaxis = {'title': "Nombre d'étrangers"},
            hovermode = 'closest',
        )
    }

    figuresImmigres = {
        'data': traces_immigres,
        'layout': go.Layout(
            title = f'Evolution de la population immigrées<br> à {ville_choisie}',
            xaxis = {'title': 'Années'},
            yaxis = {'title': "Nombre des immigrés"},
            hovermode = 'closest',
        )
    }

    return figuresEtrangers, figuresImmigres


# Répartition des étrangres et des immigrés: Cette fonction retourne 4 figures et 2 tables de données
@app.callback([Output('repartition_etrangers_HF', 'figure'), Output('repartion_etrangers_ages', 'figure'),
Output('repartition_immigres_HF', 'figure'), Output('repartion_immigres_ages', 'figure'), Output('tableau_etrangers', 'data'),
Output('tableau_etrangers', 'columns'), Output('tableau_immigres', 'data'), Output('tableau_immigres', 'columns') ], [Input('ville-picker', 'value')])
def evolution_etrangers_immigres(ville_choisie):
    colonnes_etrangers = ['Hommes étrangers', 'Femmes étrangères']
    colonnes_etrangers_ages = ['Moins de 15 ans étrangers', '15-24 ans étrangers', '25-54 ans étrangers', '55 ans et plus étrangers']
    colonnes_table_data_etrangers = ['Hommes étrangers', 'Femmes étrangères', 'Moins de 15 ans étrangers', '15-24 ans étrangers', '25-54 ans étrangers', '55 ans et plus étrangers']
    colonnes_immigrees = ['Hommes immigrés', 'Femmes immigrées']
    colonnes_immigrees_ages = ['Moins de 15 ans immigrés', '15-24 ans immigrés', '25-54 ans immigrés', '55 ans et plus immigrés']
    colonnes_table_data_immigres = ['Hommes immigrés', 'Femmes immigrées', 'Moins de 15 ans immigrés', '15-24 ans immigrés', '25-54 ans immigrés', '55 ans et plus immigrés']

    labels_etrangers = colonnes_etrangers
    labels_etrangers_ages = colonnes_etrangers_ages
    labels_immigres = colonnes_immigrees
    labels_immigres_ages = colonnes_immigrees_ages

    values_etrangers = [float(df_demographie[df_demographie['ville'] == ville_choisie][colonne].iloc[0]) for colonne in colonnes_etrangers]
    values_etrangers_ages = [float(df_demographie[df_demographie['ville'] == ville_choisie][colonne].iloc[0]) for colonne in colonnes_etrangers_ages]
    values_immigrees = [float(df_demographie[df_demographie['ville'] == ville_choisie][colonne].iloc[0]) for colonne in colonnes_immigrees]
    values_immigrees_ages = [float(df_demographie[df_demographie['ville'] == ville_choisie][colonne].iloc[0]) for colonne in colonnes_immigrees_ages]

    total_etrangers = sum(values_etrangers)
    total_immigres= sum(values_immigrees)

    traces_data_etrangers = [
        go.Pie(labels = labels_etrangers, values = values_etrangers)
    ]

    traces_data_etrangers_age = [
        go.Pie(labels = labels_etrangers_ages, values = values_etrangers_ages)
    ]

    traces_data_immigres = [
        go.Pie(labels = labels_immigres, values = values_immigrees)
    ]

    traces_data_immigres_age = [
        go.Pie(labels = labels_immigres_ages, values = values_immigrees_ages)
    ]

    ########################### Traitement des données conçernant les tables
    infos_etrangers = {
        'intitule': colonnes_table_data_etrangers,
        'donnee': [df_demographie[df_demographie['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes_table_data_etrangers]
    }

    table_donnee_etrangers = DataFrame(infos_etrangers)
    data_etrangers = table_donnee_etrangers.to_dict('rows')

    entete_etrangers = [{'id': 'intitule', 'name': 'Intitulé'}, {'id': 'donnee', 'name': ville_choisie.split('(')[0].strip()}]
    ################################################################################""
    infos_immigres = {
        'intitule': colonnes_table_data_immigres,
        'donnee': [df_demographie[df_demographie['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes_table_data_immigres]
    }

    table_donnee_immigres = DataFrame(infos_immigres)
    data_immigrees = table_donnee_immigres.to_dict('rows')

    entete_immigres = [{'id': 'intitule', 'name': 'Intitulé'}, {'id': 'donnee', 'name': ville_choisie.split('(')[0].strip()}]


    return {
        'data': traces_data_etrangers,
        'layout': go.Layout(
            title = f'Répartition des étrangers<br> (Total: {total_etrangers})',
            legend_orientation = 'h',

        )
    }, {
        'data': traces_data_etrangers_age,
        'layout': go.Layout(
            title = 'Répartition des âges des étrangers',
            legend_orientation = 'h',

        )
    }, {
        'data': traces_data_immigres,
        'layout': go.Layout(
            title = f'Répartition des immigrés<br> (Total: {total_immigres})',
            legend_orientation = 'h',

        )
    }, {
        'data': traces_data_immigres_age,
        'layout': go.Layout(
            title = f'Répartition des âges des immigrés',
            legend_orientation = 'h',

        )
    }, data_etrangers, entete_etrangers, data_immigrees, entete_immigres

################################################# ONGLET EMPLOI ############################################""
@app.callback(Output('evolution_chomage', 'figure'), [Input('ville-picker', 'value')])
def evolution_du_chomage(ville_choisie):
    x_axis = np.array(range(2004, 2017))
    y_axis = [df_chomage[df_chomage['ville'] == ville_choisie][str(annee)].iloc[0] for annee in range(2004, 2017)]
    y_mean = [df_chomage[str(annee)].mean() for annee in range(2004, 2017)]

    traces = [
        go.Scatter(x = x_axis, y = y_axis, mode = 'lines+markers', line = {'shape': 'spline', 'smoothing': 1}, name = f'Taux de chomage à {ville_choisie.split("(")[0].strip()}'),
        go.Scatter(x = x_axis, y = y_mean, mode = 'lines+markers', line = {'shape': 'spline', 'smoothing': 1}, name = 'Moyenne de France')
    ]

    return {
        'data': traces,
        'layout': go.Layout(
            title = f'Evolution du taux de chomage à {ville_choisie.split("(")[0].strip()}',
            xaxis = {'title': 'Années'},
            yaxis = dict(title='% de la population'),
            hovermode = 'closest',
        )
    }

# Part des actifs hommes et femmes
@app.callback(Output('emploi_HF', 'figure'), [Input('ville-picker', 'value')])
def emploiHF(ville_choisie):
    colonnes_homme = ['Part des actifs hommes (%)', "Taux d'activité hommes (%)", "Taux d'emploi hommes (%)", 'Taux de chômage hommes (%)']
    colonnes_femme = ['Part des actifs femmes (%)', "Taux d'activité femmes (%)", "Taux d'emploi femmes (%)", 'Taux de chômage femmes (%)']

    traces = [
        go.Bar(
            x = ['Part des actifs', "Taux d'activité", "Taux d'emploi", 'Taux de chômage'],
            y = [df_emploi[df_emploi['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes_homme],
            name = 'Hommes'
        ),

        go.Bar(
            x = ['Part des actifs', "Taux d'activité", "Taux d'emploi", 'Taux de chômage'],
            y = [df_emploi[df_emploi['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes_femme],
            name = 'Femmes'
        )
    ]

    return {
        'data': traces,
        'layout': go.Layout(
            title = f'Emploi, activité et chomage<br> des hommes et des femmes (en %) à {ville_choisie.split("(")[0].strip()}',

        )
    }

@app.callback([Output('table_emploi_HF', 'data'), Output('table_emploi_HF', 'columns')], [Input('ville-picker', 'value')])
def table_emploi_HF(ville_choisie):
    colonnes_h = ['Part des actifs hommes (%)', "Taux d'activité hommes (%)", "Taux d'emploi hommes (%)", 'Taux de chômage hommes (%)']
    colonnes_f = ['Part des actifs femmes (%)', "Taux d'activité femmes (%)", "Taux d'emploi femmes (%)", 'Taux de chômage femmes (%)']

    infos = {
        'intitule': ["Part des actifs", "Taux d'activité", "Taux d'emploi", "Taux de chômage"],
        'hommes': [df_emploi[df_emploi['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes_h],
        'femmes': [df_emploi[df_emploi['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes_f],
    }

    table_donnee = DataFrame(infos)
    data = table_donnee.to_dict('rows')

    entete = [{'id': 'intitule', 'name': ''}, {'id': 'hommes', 'name': '% Hommes'}, {'id': 'femmes', 'name': '% \Femmes'}]

    return data, entete


# Age des actifs
@app.callback(Output('emploi_age', 'figure'), [Input('ville-picker', 'value')])
def emploiHF(ville_choisie):
    colonnes_1524 = ['Part des actifs 15-24 ans (%)', "Taux d'emploi 15-24 ans (%)", 'Taux de chômage 15-24 ans (%)']
    colonnes_2554 = ['Part des actifs 25-54 ans (%)', "Taux d'emploi 25-54 ans (%)", 'Taux de chômage 25-54 ans (%)']
    colonnes_5564 = ['Part des actifs 55-64 ans (%)', "Taux d'emploi 55-64 ans (%)", 'Taux de chômage 55-64 ans (%)']

    traces = [
        go.Bar(
            x = ['Part des actifs', "Taux d'emploi", 'Taux de chômage'],
            y = [df_emploi[df_emploi['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes_1524],
            name = '15-24 ans'
        ),

        go.Bar(
            x = ['Part des actifs', "Taux d'emploi", 'Taux de chômage'],
            y = [df_emploi[df_emploi['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes_2554],
            name = '25-54 ans'
        ),

        go.Bar(
            x = ['Part des actifs', "Taux d'emploi", 'Taux de chômage'],
            y = [df_emploi[df_emploi['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes_5564],
            name = '55-64 ans'
        )
    ]

    return {
        'data': traces,
        'layout': go.Layout(
            title = f'Activité et emploi<br> selon âge (en %) à {ville_choisie.split("(")[0].strip()}',

        )
    }

# Table contenant les informations sur l'âge
@app.callback([Output('table_age', 'data'), Output('table_age', 'columns')], [Input('ville-picker', 'value')])
def table_age(ville_choisie):
    colonnes_1524 = ['Part des actifs 15-24 ans (%)', "Taux d'emploi 15-24 ans (%)", 'Taux de chômage 15-24 ans (%)']
    colonnes_2554 = ['Part des actifs 25-54 ans (%)', "Taux d'emploi 25-54 ans (%)", 'Taux de chômage 25-54 ans (%)']
    colonnes_5564 = ['Part des actifs 55-64 ans (%)', "Taux d'emploi 55-64 ans (%)", 'Taux de chômage 55-64 ans (%)']

    infos = {
        'intitule': ["Part des actifs", "Taux d'emploi", "Taux de chômage"],
        '15-24': [df_emploi[df_emploi['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes_1524],
        '25-54': [df_emploi[df_emploi['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes_2554],
        '55-64': [df_emploi[df_emploi['ville'] == ville_choisie][colonne].iloc[0] for colonne in colonnes_5564],
    }

    table_donnee = DataFrame(infos)
    data = table_donnee.to_dict('rows')

    entete = [{'id': 'intitule', 'name': ''}, {'id': '15-24', 'name': '% 15-24 ans'}, {'id': '25-54', 'name': '% 25-54 ans'}, {'id': '55-64', 'name': '% 25-54 ans'}]

    return data, entete


######################### EVOLUTION CHOMAGE SLIDER #######################
@app.callback([Output('annee', 'children'), Output('map_chomage', 'children')], [Input('slider', 'value')])
def chomage_france(annee):
    # données à renvoyer
    affichage_annee = str(annee)
    carte = f'maps\\france_chomage_{annee}.html'

    affichage_de_la_carte = html.Iframe(srcDoc = open(carte, 'r').read(), width='80%', height='800')
    return affichage_annee, affichage_de_la_carte





server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)