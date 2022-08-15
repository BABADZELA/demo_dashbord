from genericpath import isfile
import requests
# permet de faire plusieurs requete et d'accélérer celle-ci
from multiprocessing import Pool
from bs4 import BeautifulSoup as bs
import pandas as pd
from pandas import DataFrame
from pprint import pprint
import json
import csv
import os
import time
import re

colonnes = ['Ville', 'Lien', 'Jean-Luc Mélenchon', 'Emmanuel Macron', 'Marine Le Pen', 'Éric Zemmour', 'Valérie Pécresse', 
'Yannick Jadot', 'Fabien Roussel', 'Jean Lassalle', 'Nicolas Dupont-Aignan', 'Anne Hidalgo', 
'Philippe Poutou', 'Nathalie Arthaud', 'Taux de participation', "Taux d'abstention", 
'Votes blancs (en pourcentage des votes exprimés)', 'Votes nuls (en pourcentage des votes exprimés)',
'Nombre de votants']

def diff(list1, list2):
    return list(set(list1).symmetric_difference(set(list2)))

if os.path.isfile(r'dataset/election.csv'): # vérifie si le fichier est présent dans le répertoire
    tableauSante = pd.read_csv(r'dataset/election.csv')
    fichierLiensVilles = pd.read_csv(r'dataset/liensvilles.csv', sep=';')

    temp = [f'https://election-presidentielle.linternaute.com/resultats/resultat-de-la-presidentielle-a-{lien3.split("/ville/")[1]}' 
    for lien3 in fichierLiensVilles['lien']]

    listeDesLiens = diff(tableauSante['Lien'], temp)
else:
    fichierLiensVilles = pd.read_csv(r'dataset/liensvilles.csv', sep=";")
    listeLienRecuperee = fichierLiensVilles['lien']

    # Création d'un Dataframe qui contiendra les données
    tableauSante = DataFrame(columns=colonnes)
    tableauSante.to_csv(r'dataset/election.csv', index=False)

    listeDesLiens = [f'https://election-presidentielle.linternaute.com/resultats/resultat-de-la-presidentielle-a-{lien3.split("/ville/")[1]}' 
    for lien3 in fichierLiensVilles['lien']] 


def parse(lien2):
    # Initialisation d'un dictionnaire
    dico = {i : '' for i in colonnes}
    req = requests.get(lien2)
    time.sleep(2)

    if req.status_code == 200:

        with open(r'dataset/election.csv', mode='a', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=colonnes, lineterminator='\n')

            dico['Lien'] = lien2
            # construction du lien précédant avant l'insertion de /demographie
            dico['Ville'] = lien2.split('/resultat-de-la-presidentielle-a-')[1].split('/ville')[0]

            soup = bs(requests.get(lien2).content, 'html.parser')

            # divs = soup.findAll('div', class_ = 'marB20')

            # tableau = divs[6]
            tableau = soup.findAll('table', class_ = 'od_table--grid--col3 elections_table--candidats-with-pic')
            
            # candidats = tableau.findAll('table')[0].find('tbody').findAll('tr', class_ = re.compile('color'))

            if len(tableau) == 2:
                candidats = tableau[1].find('tbody').findAll('tr', class_ = re.compile('color'))
                for candidat in candidats:
                    cle = candidat.find('strong').text.replace('\n', '')
                    valeur = candidat.findAll('td')[1].text.replace(',', '.').replace('%', '').replace('\n', '').strip()
                    dico[cle] = valeur

            # infosParticipations = tableau.findAll('table')[1].find('tbody').findAll('tr')
            infosParticipations = soup.findAll('table', class_ = 'od_table--grid--col2')

            if len(infosParticipations) == 2:
                for infoParticipation in infosParticipations[1].find('tbody').findAll('tr'):
                    cle = infoParticipation.findAll('td')[0].text.replace('\n', '').strip()
                    valeur = infoParticipation.findAll('td')[1].text.replace(',', '.').replace('%', '')

                    try:
                        dico[cle] = float(valeur)
                    except:
                        dico[cle] = valeur

            writer.writerow(dico)
            print(dico)

if __name__ == "__main__":
    with Pool(30) as p:
        p.map(parse, listeDesLiens) 
