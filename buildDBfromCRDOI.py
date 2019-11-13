from habanero import Crossref
from habanero import cn
from difflib import SequenceMatcher
import pybtex.database as db
import re
import csv
import yaml

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

#use content to retrieve article data by DOI
def getCrossRefBibData(doi_text):
    art_bib = cn.content_negotiation(ids = doi_text, format = "bibentry")
    bib_yaml = db.parse_string(art_bib, 'bibtex')
    bib_dict = yaml.safe_load(bib_yaml.to_string("yaml"))
    return bib_dict


# open articles csv file
catalysis_articles = {}
fieldnames=[]
with open('UKCatalysisHubArticles201910VerCN.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         if fieldnames==[]:
             fieldnames=list(row.keys())
         catalysis_articles[int(row['Num'])]=row
         if row['Identifier'] == "":
             print("Missing Identifier", row['Title'], row['Identifier'])


# build new article and author tables
# list of articles from crossref using DOIs
cr_articles = {} # Num (from CHUK), DOI, type, and other fiedls from CR.
article_columns=["Num"]
# list of article authors from cross ref
cr_authors = {} # AuthorNum, Firstname, Middle name, Last Name
author_columns = ["AuthorNum", "FirstName", "MiddleName", "LastName"]
# list of article-author links
cr_article_authour_link = {} # AuthorNum, DOI
article_authour_columns = ["DOI","AuthorNum"]

          
for cat_art_num in catalysis_articles.keys():
    if catalysis_articles[cat_art_num]['IDVal'] != "":
        article_title = catalysis_articles[cat_art_num]['Title']
        doi_text = catalysis_articles[cat_art_num]['IDVal']
        article_data = getCrossRefBibData(doi_text)
        doi_ok = verifyArticleDOIinCrossrefCN(article_title,doi_text)
        if not doi_ok:
            if not ("doi_error" in fieldnames):
                fieldnames.append("doi_error")
            catalysis_articles[cat_art_num]['doi_error'] = doi_ok


#write back to a new csv file
with open('UKCatalysisHubArticles201910VerCN.csv', 'w', newline='') as csvfile:
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
