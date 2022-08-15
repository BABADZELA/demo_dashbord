import folium
import pandas as pd

# on récupère les données
df_elections = pd.read_csv(r'dataset/dataRecuperees/elections.csv')
df_candidats = pd.read_csv(r'dataset/dataRecuperees/candidats_2019.csv')
df_infos = pd.read_csv(r'dataset/dataRecuperees/infos.csv')

# la table des infos contient les longitudes et latitudes par contre d'autres informations sont manquantes
# Nous allons parrer à cette éventualité on supprimant toutes colonnes vides
df_infos  = df_infos[df_infos.Latitude != 'nc']
df_infos  = df_infos[df_infos.Longitude != 'nc']

liste_des_candidats = df_candidats.candidat

# on crée une nouvelle colonne gagnant dans la table des élections, on compare toutes les valeurs obtenues par chaque candidat et on
# récupère la valeur max sur les lignes
df_elections['gagnant'] = df_elections[liste_des_candidats].idxmax(axis=1)
villes = df_infos.ville.unique()

# fonctions qui fixe la couleur en fonction du candidat
def color_candidat(candidat):
    couleur = ''
    if candidat == 'Nathalie LOISEAU':
        couleur = '#EFC29D'
    elif candidat == 'Jordan BARDELLA':
        couleur = '#1C435C'
    elif candidat == 'François-Xavier BELLAMY':
        couleur = '#9AD2F6'
    elif candidat == 'Yannick JADOT':
        couleur = '#91BAFB'
    elif candidat == 'Benoît HAMON':
        couleur = '#560836'
    elif candidat == 'Manon AUBRY':
        couleur = '#EF9E9E'
    elif candidat == 'Raphaël GLUCKSMANN':
        couleur = '#E97DBD'
    elif candidat == 'Nicolas DUPONT-AIGNAN':
        couleur = '#69A0FA'

    return couleur

# Création de la map
map = folium.Map(location=[46.1076707, 3.6705597], zoom_start=6.2)

figure_ville = folium.FeatureGroup(name='Résultats des élections 2019')

comptage = 1

for ville in villes:
    try:
        latitude = df_infos[df_infos.ville == ville].Latitude.iloc[0]
        longitude = df_infos[df_infos.ville == ville].Longitude.iloc[0]
        gagnant = df_elections[df_elections.ville == ville].gagnant.iloc[0]

        figure_ville.add_child(folium.CircleMarker(
            location=[latitude, longitude],
            radius=1,
            fill_color=color_candidat(gagnant),
            color=color_candidat(gagnant),
            fill_opacity=0.7,
        ))

        map.add_child(figure_ville)
        print(comptage)
        comptage += 1
    except:
        continue
map.save(r'maps/elections_2019.html')   
