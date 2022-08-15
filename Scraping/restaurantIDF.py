from selenium import webdriver
import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup as bs
import csv
import time

# lien = 'https://ville-data.com/restaurant/ile-de-France-11R/1/1174'

colonnes = ['Nom du restaurant', 'Adresse', 'Commune', 'Détails', 'Type de commerce']

dico = {i: '' for i in colonnes}

# Création d'un Dataframe qui contiendra les données
tableauRestaurant = DataFrame(columns=colonnes)
tableauRestaurant.to_csv(r'../dataset/restaurants.csv', index=False)

listeDesLiens = [f'https://ville-data.com/restaurant/ile-de-France-11R/{i}/1174' for i in range(1, 11)]

navigateur = webdriver.Firefox(executable_path='../geckodriver.exe')
# navigateur.maximize_window()

temp = 1
for lien in listeDesLiens:
    navigateur.get(lien)
    time.sleep(3)

    if temp == 1:
        # ce bouton permet d'approuver le consentement des cookies
        if navigateur.find_element_by_xpath("//button[@class='fc-button fc-cta-consent fc-primary-button']"):
            navigateur.find_element_by_xpath("//button[@class='fc-button fc-cta-consent fc-primary-button']").click()
            temp += 1

    if navigateur.find_element_by_xpath('//article/div/div[@class="cellule"]'):
        contenuArticle = navigateur.find_element_by_xpath('//article')

        with open(r'../dataset/restaurants.csv', mode='a', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=colonnes, lineterminator='\n')
            # récupération de la donnée
            soup = bs(navigateur.page_source, 'html.parser')

            divsArticles = soup.find('article').findAll('div', {'style': 'border-collapse:collapse; font-size: 1em; border: solid 1px #aaa; line-height: 1.167em;margin:10px;margin-left:0px;color:#656565;text-align:left;width:100%; min-height : 160px;font-size:1.2em; margin-top:0px;box-shadow: 3px 8px 12px #aaa; padding-left:3px; padding-right:3px;'})

            for div in divsArticles:
                divCellule = div.findAll('div', {'class': 'cellule'})

                if len(divCellule) == 6:
                    for i in range(1, len(divCellule)+1):

                        if i == 1:               
                            nomRestaurant = divCellule[0].find('strong').text
                            commune = divCellule[0].find('div', {
                                'style': 'text-transform:uppercase; text-align:right; color:#656565;margin-right:5px;'
                                }
                            ).text.replace('\n', '').strip()
                            dico['Nom du restaurant'] = nomRestaurant
                            dico['Commune'] = commune
                        elif i == 2:
                            continue
                        elif i == 3:
                            dico['Type de commerce'] = divCellule[2].text
                        elif i== 4:
                            dico['Adresse'] = divCellule[3].text
                        elif i == 5:
                            continue
                        elif i== 6:
                            dico['Détails'] = divCellule[5].text
                    
                    writer.writerow(dico)
                    print(dico)

                elif len(divCellule) == 5:    
                    for i in range(1, len(divCellule)+1):            
                        if i == 1:               
                            nomRestaurant = divCellule[0].find('strong').text
                            commune = divCellule[0].find('div', {
                                'style': 'text-transform:uppercase; text-align:right; color:#656565;margin-right:5px;'
                                }
                            ).text.replace('\n', '').strip()
                            dico['Nom du restaurant'] = nomRestaurant
                            dico['Commune'] = commune
                        elif i == 2:
                            continue
                        elif i == 3:
                            dico['Type de commerce'] = divCellule[2].text
                        elif i== 4:
                            continue
                        elif i== 5:
                            dico['Détails'] = divCellule[4].text

                    writer.writerow(dico)
                    print(dico)


        

            




