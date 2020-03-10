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
    

###############################################################################
# open articles csv file
###############################################################################

input_file = 'UKCH201911DOIOnly.csv'
catalysis_articles = {}
fieldnames=[]
with open(input_file, newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         if fieldnames==[]:
             fieldnames=list(row.keys())
         catalysis_articles[int(row['Num'])]=row
         if row['DOI'] == "":
             print("Missing Identifier", row['Title'], row['Identifier'])


# build new article and author tables
# list of articles from crossref using DOIs
cr_articles = {} # Num (from CHUK), DOI, type, and other fiedls from CR.
article_columns=["NumUKCH"]
# list of article authors from cross ref
cr_authors = {} # AuthorNum, Firstname, Middle name, Last Name
author_columns = ["AuthorNum", "Name", "LastName", "ORCID", 'affiliations','sequence']
# list of article-author links
cr_article_authour_link = {} # AuthorNum, DOI
article_authour_columns = ["DOI","AuthorNum"]

## NumUKCH 	        : 1
## indexed 	        : [2019, 11, 11]
## reference-count 	: 52
## publisher 	        : Springer Science and Business Media LLC
## issue 	        : 10
## license 	        : http://www.springer.com/tdm
## funder 	        : None
## content-domain 	: None
## published-print 	: [2019, 10]
## DOI 	                : 10.1038/s41929-019-0334-3
## type 	        : article-journal
## created 	        : [2019, 9, 16]
## page 	        : 873-881
## update-policy 	: http://dx.doi.org/10.1007/springer_crossmark_policy
## source 	        : Crossref
## is-referenced-by-count : 0
## title 	        : Tuning of catalytic sites in Pt/TiO2 catalysts for the chemoselective hydrogenation of 3-nitrostyrene
## prefix 	        : 10.1038
## volume 	        : 2
## member 	        : 297
## published-online 	: [2019, 9, 16]
## reference 	        : None
## container-title 	: Nature Catalysis
## original-title 	: None
## language 	        : en
## link        	        : http://www.nature.com/articles/s41929-019-0334-3.pdf
## deposited 	        : [2019, 11, 11]
## score 	        : 1.0
## subtitle 	        : None
## short-title 	        : None
## issued        	: [2019, 9, 16]
## references-count 	: 52
## journal-issue 	: None
## alternative-id 	: None
## URL 	                : http://dx.doi.org/10.1038/s41929-019-0334-3
## relation 	        : None
## ISSN 	        : None
## container-title-short : Nat Catal
          
for cat_art_num in catalysis_articles.keys():
    if catalysis_articles[cat_art_num]['DOI'] != "":
        doi_text = catalysis_articles[cat_art_num]['DOI']
        article_data = getCrossRefBibData(doi_text)
        data_keys = list(article_data.keys())
        for key in data_keys:
            if not (key in article_columns) and \
               key not in ['author', 'assertion', 'indexed', 'funder',
                           'content-domain','created','update-policy', 'source',
                           'is-referenced-by-count','prefix','member',
                           'reference','original-title','language','deposited',
                           'score', 'subtitle', 'short-title', 'issued',
                           'alternative-id','relation','ISSN','container-title-short']:
                article_columns.append(key)
        #print(article_columns)
        new_row = {}
        
        for key in article_columns:
            if key == 'NumUKCH':
                new_row['NumUKCH'] = cat_art_num
            else:
                if key in article_data.keys():
                    new_row[key] = jsonToPlainText(article_data[key])
        #print(new_row)
        cr_articles[cat_art_num] = new_row
        #print(cr_articles)
        for author in article_data['author']:
            new_author={}
            aut_num = len(cr_authors) + 1
            new_author["AuthorNum"] = aut_num
            new_author['LastName'] = author['family']
            if 'given' in author.keys():
                new_author['Name'] = author['given']
            if 'given' in author.keys():
                new_author['sequence'] = author['sequence']
            if 'ORCID' in author.keys():
            	new_author['ORCID'] = author['ORCID']
            else:
                new_author['ORCID'] = "None"
            if 'affiliation'in author.keys():
                affiliations=""
                for affl in author['affiliation']:
                    affiliations += affl['name'] + "|"
                new_author['affiliations'] = affiliations
            cr_authors[aut_num] = new_author
            art_auth_link = len(cr_article_authour_link)+1
            new_art_auth_link={}
            new_art_auth_link['DOI'] = doi_text
            new_art_auth_link['AuthorNum'] = aut_num
            cr_article_authour_link[art_auth_link] = new_art_auth_link
        print(article_data['author'])
        
        
    
# write back to a new csv file
# create three files

with open('UKCCHArticles201911.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = article_columns)
    writer.writeheader()
    for cat_art_num in cr_articles.keys():
        writer.writerow(cr_articles[cat_art_num])

with open('UKCCHAuthors201911.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = author_columns)
    writer.writeheader()
    for aut_num in cr_authors.keys():
        writer.writerow(cr_authors[aut_num])


with open('UKCCHArtAutLink201911.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = article_authour_columns)
    writer.writeheader()
    for link_num in cr_article_authour_link.keys():
        writer.writerow(cr_article_authour_link[link_num])

        
