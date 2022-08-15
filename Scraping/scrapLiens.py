import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from pandas import DataFrame
import csv

lien = 'https://www.journaldunet.com/management/ville/seine-et-marne/departement-77/villes'

content = bs(requests.get(lien).content, 'html.parser')
tousLesLiens = content.findAll('a')

# Préparation des données
colonnes = ['ville', 'lien']

""" tableau = DataFrame(columns=colonnes)
tableau.to_csv('dataset\\liensvilles.csv', index=False) """


data = {}
data['ville'] = ''
data['lien'] = ''

with open('dataset\\liensvilles.csv', 'a', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=colonnes, lineterminator='\n')
    for lien in tousLesLiens:
        if '/ville-' in lien['href']:
            data['lien'] = lien['href']
            data['ville'] = lien.text
            
            writer.writerow(data)