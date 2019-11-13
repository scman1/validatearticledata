from habanero import Crossref
from difflib import SequenceMatcher
import re
import csv

def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()

cr = Crossref()


def getArticleDOIFromCrossref(article_title):
    res = cr.works(query = article_title, select = ["DOI","title"])
    doi_text=""
    try:
        for recovered in res['message']['items']:
            similarity = similar(recovered['title'][0], article_title)
            #print(recovered['title'][0], similarity)
            if similarity > 0.9:
                doi_text = recovered['DOI']
    except:
        doi_text=""
    return doi_text




# open articles csv file
catalysis_articles = {}
with open('UKCatalysisHubArticles201910.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         catalysis_articles[int(row['Num'])]=row
         if row['Identifier'] == "":
            print(row['Title'], row['Identifier'])


#fill in the missing identifier
for cat_art_num in catalysis_articles.keys():
    if catalysis_articles[cat_art_num]['Identifier'] =="":
        article_title = catalysis_articles[cat_art_num]['Title']
        doi_text=getArticleDOIFromCrossref(article_title)
        catalysis_articles[cat_art_num]['Identifier'] = doi_text


#write back to a new csv file
with open('UKCatalysisHubArticles201910Mod.csv', 'w', newline='') as csvfile:
    fieldnames = ['Num', 'Phase', 'P', 'CatalysisTheme', 'ProjectYear', 'Authors', 'Title', 'Journal', 'PublicationDate', 'Identifier']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for cat_art_num in catalysis_articles.keys():
        writer.writerow(catalysis_articles[cat_art_num])
