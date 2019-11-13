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

def verifyArticleDOIinCrossref(article_title,doi_text):
    res = cr.works(query = doi_text, select = ["DOI","title"])
    doi_match=False
    try:
        for recovered in res['message']['items']:
            similarity = similar(recovered['title'][0], article_title)
            #print(recovered['title'][0], similarity)
            if similarity > 0.9:
                doi_match=True
                break
            else:
                print("Difference",similarity, article_title, recovered['title'][0])
    except:
        doi_match=False
    return doi_match


# open articles csv file
catalysis_articles = {}
fieldnames=[]
with open('UKCatalysisHubArticles201910Mod.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         if fieldnames==[]:
             fieldnames=list(row.keys())
         catalysis_articles[int(row['Num'])]=row
         if row['Identifier'] == "":
             print(row['Title'], row['Identifier'])


#fill in the missing identifier
for cat_art_num in catalysis_articles.keys():
    if catalysis_articles[cat_art_num]['IDVal'] != "":
        article_title = catalysis_articles[cat_art_num]['Title']
        doi_text = catalysis_articles[cat_art_num]['IDVal']
        doi_ok = verifyArticleDOIinCrossref(article_title,doi_text)
        if not doi_ok:
            if not ("doi_error" in fieldnames):
                fieldnames.append("doi_error")
            catalysis_articles[cat_art_num]['doi_error'] = doi_ok


#write back to a new csv file
with open('UKCatalysisHubArticles201910Ver.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for cat_art_num in catalysis_articles.keys():
        writer.writerow(catalysis_articles[cat_art_num])
