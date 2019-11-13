from habanero import Crossref
from habanero import cn
from difflib import SequenceMatcher
import pybtex.database as db
import re
import csv
import yaml
import json

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

#use works to find articles by key
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

#use content to find articles by key
def verifyArticleDOIinCrossrefCN(article_title,doi_text):
    art_bib = cn.content_negotiation(ids = doi_text, format = "bibentry")
    
    bib_yaml = db.parse_string(art_bib, 'bibtex')
    
    bib_dict = yaml.safe_load(bib_yaml.to_string("yaml"))
    entries_list = list(bib_dict['entries'].keys())
    doi_match=False
    if  len(entries_list) > 1:
        print("Warning ID with multiple entries")
    try:
        for entry in entries_list:
            bib_title = bib_dict['entries'][entry]['title']
            bib_doi = bib_dict['entries'][entry]['doi']
            similarity = similar(bib_title, article_title)
            if similarity > 0.9:
                doi_match=True
                break
            else:
                print("Difference|",similarity, "|", article_title, "|", doi_text, "|", bib_title, "|", bib_doi)
    except:
        doi_match=False
    return doi_match

# Use content to retrieve article data by DOI
# would be better to use json but somehow it is slower than bibentry+RIS
def getCrossRefBibData(doi_text):
    try:
        art_bib = json.loads(cn.content_negotiation(ids = doi_text, format = "citeproc-json"))
        return art_bib
    except:
        return {}

def jsonToPlainText(element):
    if isinstance(element, int) or \
       isinstance(element, float) or \
       isinstance(element, str):
        return element
    elif 'date-parts' in element:
        return element['date-parts'][0]
    elif 'issue' in element:
        return element['issue']
    elif isinstance(element, list) \
         and len(element) > 0 and 'URL' in element[0]:
        return element[0]['URL']
    

###########################################################################################
# open articles csv files
catalysis_articles = {}
fieldnames=[]
with open('UKCatalysisHubArticles201910VerCN.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         if fieldnames==[]:
             fieldnames=list(row.keys())
         catalysis_articles[int(row['Num'])]=row
         
fieldnames.append('similarity')
fieldnames.append('CRTitle')

cr_articles = {}
article_columns=[]

with open('UKCCHArticles201910CR.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         if article_columns==[]:
             article_columns=list(row.keys())
         cr_articles[int(row['NumUKCH'])]=row

for cat_art_num in cr_articles.keys():
    ch_title = catalysis_articles[cat_art_num]['Title']
    cr_title = cr_articles[cat_art_num]['title']
    similarity = similar(ch_title,cr_title)
    catalysis_articles[cat_art_num]['similarity'] = similarity
    catalysis_articles[cat_art_num]['CRTitle'] = cr_title
    
# write back to a new csv file
# create three files

with open('UKCatalysisHubArticles201910VerTitles.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()
    for cat_art_num in catalysis_articles.keys():
        writer.writerow(catalysis_articles[cat_art_num])
