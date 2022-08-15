from genericpath import isfile
import requests
# permet de faire plusieurs requete et d'accélérer celle-ci
from multiprocessing import Pool
from bs4 import BeautifulSoup as bs
import pandas as pd
from pandas import DataFrame
import csv
import os
import time

# Création d'une fonction qui permet de reprendre le téléchargement des données après avoir perdu la connexion
def diff(list1, list2):
    return list(set(list1).symmetric_difference(set(list2)))

colonnes = ['ville', 'lien', 'Région', 'Département', 'Etablissement public de coopération intercommunale (EPCI)',
'Code postal (CP)', 'Code Insee', 'Nom des habitants', 'Population (2018)', 'Population : rang national (2018)', 
'Densité de population (2018)', 'Taux de chômage (2018)', 'Pavillon bleu', "Ville d'art et d'histoire", 
'Ville fleurie', 'Ville internet', 'Superficie (surface)', 'Altitude min.', 'Altitude max.', 'Latitude', 'Longitude']

if os.path.isfile(r'dataset/infos.csv'): # vérifie si le fichier est présent dans le répertoire
    tableauInfos = pd.read_csv(r'dataset/infos.csv')
    fichierLiensVilles = pd.read_csv(r'dataset/liensvilles.csv', sep=';')

    listeLienRecuperee = diff(tableauInfos['lien'], fichierLiensVilles['lien'])
else:
    fichierLiensVilles = pd.read_csv('dataset\\liensvilles.csv', sep=";")
    listeLienRecuperee = fichierLiensVilles['lien']

    # Création d'un Dataframe qui contiendra les données
    tableauInfos = DataFrame(columns=colonnes)
    tableauInfos.to_csv(r'dataset/infos.csv', index=False)

print(listeLienRecuperee)

def parse(lien):
    # Initialisation d'un dictionnaire
    result = {i : '' for i in colonnes}
    req = requests.get(lien)
    time.sleep(2)

    if req.status_code == 200:

        with open(r'dataset/infos.csv', mode='a', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=colonnes, lineterminator='\n')

            # for lien in listeLienRecuperee:
            result['lien'] = lien
            result['ville'] = fichierLiensVilles[fichierLiensVilles['lien'] == lien]['ville'].iloc[0]

            content = bs(req.content, 'html.parser')
            tables = content.findAll('table', class_ = 'odTable odTableAuto')

            for table in tables:
                for data in table.findAll('tr')[1:]:
                    cle = data.findAll('td')[0].text
                    valeur = data.findAll('td')[1].text

            # cette condition permet d'uniformiser les résultats et ne pas avoir Nom des habitants de Paris etc..
                    if 'Nom des habitants' in cle:
                        result['Nom des habitants'] = valeur
                    elif 'Taux de chômage' in cle:
                        result['Taux de chômage (2018)'] = valeur
                    else:
                        result[cle] = valeur
            writer.writerow(result)
            print(lien) 


if __name__ == "__main__":
    with Pool(30) as p:
        p.map(parse, listeLienRecuperee) 

