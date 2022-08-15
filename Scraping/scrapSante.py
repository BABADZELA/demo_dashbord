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

listeCles = ['Ville', 'Lien', 'Allocataires CAF', 'Bénéficiaires du RSA', ' - bénéficiaires du RSA majoré',
 ' - bénéficiaires du RSA socle', "Bénéficiaires de l'aide au logement", 
 " - bénéficiaires de l'APL (aide personnalisée au logement)", 
 " - bénéficiaires de l'ALF (allocation de logement à caractère familial)", 
 " - bénéficiaires de l'ALS (allocation de logement à caractère social)", 
 " - bénéficiaires de l'Allocation pour une location immobilière", 
 " - bénéficiaires de l'Allocation pour un achat immobilier", 'Bénéficiaires des allocations familiales', 
 ' - bénéficiaires du complément familial', " - bénéficiaires de l'allocation de soutien familial", 
 " - bénéficiaires de l'allocation de rentrée scolaire", 'Médecins généralistes', 'Masseurs-kinésithérapeutes', 
 'Dentistes', 'Infirmiers', 'Spécialistes ORL', 'Ophtalmologistes', 'Dermatologues', 'Sage-femmes', 'Pédiatres', 
 'Gynécologues', 'Pharmacies', 'Urgences', 'Ambulances', 'Etablissements de santé de court séjour', 
 'Etablissements de santé de moyen séjour', 'Etablissements de santé de long séjour', 
 "Etablissement d'accueil du jeune enfant", 'Maisons de retraite', 'Etablissements pour enfants handicapés', 
 'Etablissements pour adultes handicapés', 'Bénéficiaires de la PAJE', 
 " - bénéficiaires de l'allocation de base", 
 ' - bénéficiaires du complément mode de garde pour une assistante maternelle', 
 " - bénéficiaires du complément de libre choix d'activité (CLCA ou COLCA)", 
 ' - bénéficiaires de la prime naissance ou adoption']

# la variable dico va contenir toutes valeurs de la listes des clés et recevra des valeurs supplémentaires.
# la concaténation entre plusieurs dictionnaires est faite avec * commme ci-dessous.
dico = {
    **{i : '' for i in listeCles},
    **{"nbre allocataires (" + str(a) + ")" : '' for a in range(2009, 2021)},
    **{"nbre RSA (" + str(a) + ")" : '' for a in range(2009, 2021)},
    **{"nbre APL (" + str(a) + ")" : '' for a in range(2009, 2021)},
    **{"nbre Alloc Familiales (" + str(a) + ")" : '' for a in range(2009, 2021)},
}

# création des colonnes pour les données à récupérer
colonnes = list(dico.keys())

def diff(list1, list2):
    return list(set(list1).symmetric_difference(set(list2)))

if os.path.isfile(r'dataset/santeSocial.csv'): # vérifie si le fichier est présent dans le répertoire
    tableauSante = pd.read_csv(r'dataset/santeSocial.csv')
    fichierLiensVilles = pd.read_csv(r'dataset/liensvilles.csv', sep=';')

    temp = [f'{lien3}/sante-social' for lien3 in fichierLiensVilles['lien']]

    listeDesLiens = diff(tableauSante['Lien'], temp)
else:
    fichierLiensVilles = pd.read_csv(r'dataset/liensvilles.csv', sep=";")
    listeLienRecuperee = fichierLiensVilles['lien']

    # Création d'un Dataframe qui contiendra les données
    tableauSante = DataFrame(columns=colonnes)
    tableauSante.to_csv(r'dataset/santeSocial.csv', index=False)

    listeDesLiens = [f'{lien3}/sante-social' for lien3 in listeLienRecuperee]


def parse(lien2):
    # Initialisation d'un dictionnaire
    dico = {
        **{i : '' for i in listeCles},
        **{"nbre allocataires (" + str(a) + ")" : '' for a in range(2009, 2021)},
        **{"nbre RSA (" + str(a) + ")" : '' for a in range(2009, 2021)},
        **{"nbre APL (" + str(a) + ")" : '' for a in range(2009, 2021)},
        **{"nbre Alloc Familiales (" + str(a) + ")" : '' for a in range(2009, 2021)},
    }
    req = requests.get(lien2)
    time.sleep(2)

    if req.status_code == 200:

        with open(r'dataset/santeSocial.csv', mode='a', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=colonnes, lineterminator='\n')

            req = requests.get(lien2)
            contenu = req.content
            soup = bs(contenu, 'html.parser')

            dico['Lien'] = lien2
            # construction du lien précédant avant l'insertion de /demographie
            lienReconstruit = lien2.split('/sante-social')[0]
            dico['Ville'] = fichierLiensVilles[fichierLiensVilles['lien'] == lienReconstruit]['ville'].iloc[0]

            tables = soup.findAll('table', class_ = "odTable odTableAuto")

            # récupération tableaux présents sur les pages
            for table in tables:
                for tr in table.findAll('tr')[1:]:
                    cle = tr.findAll('td')[0].text
                    valeur = tr.findAll('td')[1].text
                    try:
                        dico[cle] = float(''.join(valeur.split()))
                    except:
                        dico[cle] = valeur

            divs = soup.findAll('div', class_ = 'hidden marB20')

            for div in divs:
                titre_h2 = div.find('h2')
                if titre_h2 != None and "Nombre d'allocataires" in titre_h2.text:
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
                                dico["nbre allocataires (" + str(annee) + ")"] = float(donnee)
                            except:
                                dico["nbre allocataires (" + str(annee) + ")"] = ''

                elif titre_h2 != None and "Nombre de bénéficiaires du RSA " in titre_h2.text:
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
                                dico["nbre RSA (" + str(annee) + ")"] = float(donnee)
                            except:
                                dico["nbre RSA (" + str(annee) + ")"] = ''

                elif titre_h2 != None and "Nombre de bénéficiaires de l'aide au logement" in titre_h2.text:
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
                                dico["nbre APL (" + str(annee) + ")"] = float(donnee)
                            except:
                                dico["nbre APL (" + str(annee) + ")"] = ''

                elif titre_h2 != None and "Nombre de bénéficiaires des allocations familiales" in titre_h2.text:
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
                                dico["nbre Alloc Familiales (" + str(annee) + ")"] = float(donnee)
                            except:
                                dico["nbre Alloc Familiales (" + str(annee) + ")"] = ''
            writer.writerow(dico)
            print(dico)

if __name__ == "__main__":
    with Pool(30) as p:
        p.map(parse, listeDesLiens) 