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

listeCles = ['Ville', 'Lien', 'Population', 'Densité de population', 'Nombre de ménages', 'Habitants par ménage', 
'Nombre de familles', 'Naissances', 'Décès', 'Solde naturel', 'Hommes', 'Femmes', 'Moins de 15 ans', 
'15 - 29 ans', '30 - 44 ans', '45 - 59 ans', '60 - 74 ans', '75 ans et plus', 'Familles monoparentales', 
'Couples sans enfant', 'Couples avec enfant', 'Familles sans enfant', 'Familles avec un enfant', 
'Familles avec deux enfants', 'Familles avec trois enfants', 'Familles avec quatre enfants ou plus',
'Personnes célibataires', 'Personnes mariées', 'Personnes divorcées', 'Personnes veuves', 
'Personnes en concubinage', 'Personnes pacsées', 'Population étrangère', 'Hommes étrangers', 
'Femmes étrangères', 'Moins de 15 ans étrangers', '15-24 ans étrangers', '25-54 ans étrangers', 
'55 ans et plus étrangers', 'Population immigrée', 'Hommes immigrés', 'Femmes immigrées', 
'Moins de 15 ans immigrés', '15-24 ans immigrés', '25-54 ans immigrés', '55 ans et plus immigrés']

# la variable dico va contenir toutes valeurs de la listes des clés et recevra des valeurs supplémentaires.
# la concaténation entre plusieurs dictionnaires est faite avec * commme ci-dessous.
dico = {
    **{i : '' for i in listeCles},
    **{"nbre habitants (" + str(a) + ")" : '' for a in range(2006, 2019)},
    **{"nbre naissances (" + str(a) + ")" : '' for a in range(1999, 2020)},
    **{"nbre deces (" + str(a) + ")" : '' for a in range(1999, 2020)},
    **{"nbre étrangers (" + str(a) + ")" : '' for a in range(2006, 2019)},
    **{"nbre immigrés (" + str(a) + ")" : '' for a in range(2006, 2019)},
}

# création des colonnes pour les données à récupérer
colonnes = list(dico.keys())

def diff(list1, list2):
    return list(set(list1).symmetric_difference(set(list2)))

if os.path.isfile(r'dataset/demographie.csv'): # vérifie si le fichier est présent dans le répertoire
    tableauDemo = pd.read_csv(r'dataset/demographie.csv')
    fichierLiensVilles = pd.read_csv(r'dataset/liensvilles.csv', sep=';')

    temp = [f'{lien3}/demographie' for lien3 in fichierLiensVilles['lien']]

    listeDesLiens = diff(tableauDemo['Lien'], temp)
else:
    fichierLiensVilles = pd.read_csv(r'dataset/liensvilles.csv', sep=";")
    listeLienRecuperee = fichierLiensVilles['lien']

    # Création d'un Dataframe qui contiendra les données
    tableauDemo = DataFrame(columns=colonnes)
    tableauDemo.to_csv(r'dataset/demographie.csv', index=False)

    listeDesLiens = [f'{lien3}/demographie' for lien3 in listeLienRecuperee]

def parse(lien2):
    # Initialisation d'un dictionnaire
    dico = {
        **{i : '' for i in listeCles},
        **{"nbre habitants (" + str(a) + ")" : '' for a in range(2006, 2019)},
        **{"nbre naissances (" + str(a) + ")" : '' for a in range(1999, 2020)},
        **{"nbre deces (" + str(a) + ")" : '' for a in range(1999, 2020)},
        **{"nbre étrangers (" + str(a) + ")" : '' for a in range(2006, 2019)},
        **{"nbre immigrés (" + str(a) + ")" : '' for a in range(2006, 2019)},
    }
    req = requests.get(lien2)
    time.sleep(2)

    if req.status_code == 200:

        with open(r'dataset/demographie.csv', mode='a', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=colonnes, lineterminator='\n')
            contenu = bs(req.content, 'html.parser')
            tables = contenu.findAll('table', class_ = 'odTable odTableAuto')

            dico['Lien'] = lien2
            # construction du lien précédant avant l'insertion de /demographie
            lienReconstruit = lien2.split('/demographie')[0]
            dico['Ville'] = fichierLiensVilles[fichierLiensVilles['lien'] == lienReconstruit]['ville'].iloc[0]

            # récupération des éléments de la liste de clés
            for table in tables:
                for tr in table.findAll('tr')[1:]:
                    cle = tr.findAll('td')[0].text.split('(')[0].strip()
                    # la valeur n'est parfois pas renseignée d'où le try except
                    valeur = tr.findAll('td')[1].text.split('h')[0].strip().replace('\xa0', '').replace(',', '.')

                    try:
                        dico[cle] = float(valeur)
                    except:
                        dico[cle] = valeur

            # récupération des divs contenant les valeurs de variation démographique
            divs = contenu.findAll('div', class_ = 'hidden marB20')

            for div in divs:
                titre_h2 = div.find('h2')
                if titre_h2 != None and "Nombre d'habitants" in titre_h2.text:
                    # il arrive très souvent que le h2 existe et pas le tableau montrant l'évolution d'où le 2e if.
                    if div.find('script').string:
                        js_script = div.find('script').string
                        json_data = json.loads(js_script)
                        donnees = json_data['series'][0]['data']
                        annees = json_data['xAxis']['categories']

                        for annee, donnee in zip(annees, donnees):
                            # il arrive parfois que le nombre l'évolution du nombre d'habitant soit manquante pour d'autres années
                            # c'est pour cette raison que l'on fait un try except.
                            try:
                                dico["nbre habitants (" + str(annee) + ")"] = float(donnee)
                            except:
                                dico["nbre habitants (" + str(annee) + ")"] = ''
                        

                elif titre_h2 != None and "Naissances et décès" in titre_h2.text:
                    if div.find('script').string:
                        js_script = div.find('script').string
                        json_data = json.loads(js_script)

                        if len(json_data['series']) >= 2:
                            naissances = json_data['series'][0]['data']
                            annees = json_data['xAxis']['categories']
                            decess = json_data['series'][1]['data']

                            for annee, naissance, deces in zip(annees, naissances, decess):
                                try:
                                    dico["nbre naissances (" + str(annee) + ")"] = float(naissance)
                                    dico["nbre deces (" + str(annee) + ")"] = float(deces)
                                except:
                                    dico["nbre naissances (" + str(annee) + ")"] = ''
                                    dico["nbre deces (" + str(annee) + ")"] = ''
                        else:
                            dico["nbre naissances (" + str(annee) + ")"] = ''
                            dico["nbre deces (" + str(annee) + ")"] = ''

                elif titre_h2 != None and "Nombre d'étrangers" in titre_h2.text:
                    if div.find('script').string:
                        js_script = div.find('script').string
                        json_data = json.loads(js_script)
                        annees = json_data['xAxis']['categories']
                        etrangers = json_data['series'][0]['data']

                        for annee, etranger in zip(annees, etrangers):
                            try:
                                dico["nbre étrangers (" + str(annee) + ")"] = float(etranger)
                            except:
                                dico["nbre étrangers (" + str(annee) + ")"] = ''

                elif titre_h2 != None and "Nombre d'immigrés" in titre_h2.text:
                    if div.find('script').string:
                        js_script = div.find('script').string
                        json_data = json.loads(js_script)
                        annees = json_data['xAxis']['categories']
                        immigrers = json_data['series'][0]['data']

                        for annee, immigrer in zip(annees, immigrers):
                            try:
                                dico["nbre immigrés (" + str(annee) + ")"] = float(immigrer)
                            except:
                                dico["nbre immigrés (" + str(annee) + ")"] = ''

            writer.writerow(dico)
            print(dico)

if __name__ == "__main__":
    with Pool(30) as p:
        p.map(parse, listeDesLiens) 

