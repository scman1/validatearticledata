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

#use content to find articles by key
def verifyArticleDOIinCrossrefCN(article_title,doi_text):
    article_data = getCrossRefBibData(doi_text)
    cr_title = cr_doi = ""
    doi_match = False
    similarity = 0    
    if not article_data == {}:
        cr_title = jsonToPlainText(article_data['title'])
        cr_doi = jsonToPlainText(article_data['DOI'])
        similarity = similar(cr_title, article_title)
        if similarity > 0.9:
            doi_match=True
        else:
            print("Difference|",similarity, "|", article_title, "|", doi_text, "|", cr_title, "|", cr_doi)
    return [doi_match, cr_title, cr_doi, similarity]


# open articles csv file
input_file = 'UKCH201911cDOIV1.csv'
output_file = 'UKCH201911cDOIV1.csv'
catalysis_articles = {}
fieldnames=[]
with open(input_file, newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         if fieldnames==[]:
             fieldnames=list(row.keys())
         catalysis_articles[int(row['CatArtNum'])]=row
         if row['UniqueDOI'] == "":
             print(row['Title'], row['UniqueDOI'])


#validate the identifier
for cat_art_num in catalysis_articles.keys():
    if catalysis_articles[cat_art_num]['UniqueDOI'] != "" and \
       catalysis_articles[cat_art_num]['doi_OK'] == 'False':
        article_title = catalysis_articles[cat_art_num]['Title']
        doi_text = catalysis_articles[cat_art_num]['UniqueDOI']
        doi_ok = verifyArticleDOIinCrossrefCN(article_title,doi_text)
        if not ("doi_OK" in fieldnames):
            fieldnames.append("doi_OK")
            fieldnames.append("cr_title")
            fieldnames.append("cr_doi")
            fieldnames.append("similarity")
        catalysis_articles[cat_art_num]['doi_OK'] = doi_ok[0]
        if catalysis_articles[cat_art_num]['cr_title']=="None":
            catalysis_articles[cat_art_num]['cr_title'] = doi_ok[1]
            catalysis_articles[cat_art_num]['cr_doi'] = doi_ok[2]
            print(doi_text, article_title)
        catalysis_articles[cat_art_num]['similarity'] = doi_ok[3]
        

#write back to a new csv file
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for cat_art_num in catalysis_articles.keys():
        writer.writerow(catalysis_articles[cat_art_num])



####
##from habanero import cn
##import pybtex
##import yaml
##
##a = cn.content_negotiation(ids = "10.1038/s41929-019-0334-3", format = "bibentry")
##bd=pybtex.database.parse_string(a, 'bibtex')
##print(bd.to_string("yaml"))
##x = yaml.safe_load(bd.to_string("yaml"))
### read number of entries, should be 1, raise warning if more than one entry returned
##if  len(list(x['entries'].keys())) > 1:
##    print("Warning ID with multiple entries")
