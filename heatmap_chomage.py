import folium
import pandas as pd

# on récupère les données
df_chomage = pd.read_csv(r'dataset/dataRecuperees/chomage.csv')
df_infos = pd.read_csv(r'dataset/dataRecuperees/infos.csv')

# la table des infos contient les longitudes et latitudes par contre d'autres informations sont manquantes
# Nous allons parrer à cette éventualité on supprimant toutes colonnes vides
df_infos  = df_infos[df_infos.Latitude != 'nc']
df_infos  = df_infos[df_infos.Longitude != 'nc']
villes = df_infos.ville.unique()

def color_rate(taux):
    couleur = ''
    if taux < 7.8:
        couleur = '#FED976'
    elif 7.8 <= taux < 8.8:
        couleur = '#FC8C3C'
    elif 8.8 <= taux < 9.2:
        couleur = '#F84F38'
    elif 9.2 <= taux < 9.6:
        couleur = '#E43932'
    elif 9.6 <= taux < 10.5:
        couleur = '#BE2E28'
    elif taux >= 10.5:
        couleur = '#801F27'
    return couleur


# Création de la map
for annee in range(2004, 2017):
    map = folium.Map(location=[46.1076707, 3.6705597], zoom_start=6.2)

    figure_ville = folium.FeatureGroup(name='Taux de chômage')

    comptage = 1
    for ville in villes:
        try:
            latitude = df_infos[df_infos.ville == ville].Latitude.iloc[0]
            longitude = df_infos[df_infos.ville == ville].Longitude.iloc[0]
            taux = df_chomage[df_chomage.ville == ville][str(annee)].iloc[0]

            figure_ville.add_child(folium.CircleMarker(
                location=[latitude, longitude],
                radius=1,
                fill_color=color_rate(taux),
                color=color_rate(taux),
                fill_opacity=0.7,
            ))

            map.add_child(figure_ville)
            print(comptage)
            comptage += 1
        except:
            continue


    legend_html = '''
        <div style='position: fixed; bottom: 50px; left: 50px; width: 15%; height: 300px;
            border: 2px solid grey; z-index: 99999; font-size: 14px'>
            &nbsp; Taux de chômage en France (en %) <br><br>
            <i class="fa fa-square fa-2x"
                            style="color: #FED976"></i>&nbsp; moins de 7.8 &nbsp; <br>
            <i class="fa fa-square fa-2x"
                            style="color: #FEB24C"></i>&nbsp; entre 7.8 et 8.3 &nbsp; <br>
            <i class="fa fa-square fa-2x"
                            style="color: #FC8C3C"></i>&nbsp; entre 8.3 et 8.8 &nbsp; <br>
            <i class="fa fa-square fa-2x"
                            style="color: #F84F38"></i>&nbsp; entre 8.8 et 9.2 &nbsp; <br>
            <i class="fa fa-square fa-2x"
                            style="color: #E43932"></i>&nbsp; entre 9.2 et 9.6 &nbsp; <br>
            <i class="fa fa-square fa-2x"
                            style="color: #BE2E28"></i>&nbsp; entre 9.6 et 10.5 &nbsp; <br>
            <i class="fa fa-square fa-2x"
                            style="color: #801F27"></i>&nbsp; plus de 10.5 &nbsp;
        </div>
    '''

    map.get_root().html.add_child(folium.Element(legend_html))
    map.save(f'maps\\france_chomage_{annee}.html')  