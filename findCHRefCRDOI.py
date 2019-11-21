from habanero import Crossref
from habanero import cn
from difflib import SequenceMatcher
import pybtex.database as db
import re
import csv
import yaml
import json
import urllib

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

def findURIFrag(uri, referents, contains):
    result = ""
    try:
        req = urllib.request.Request(uri)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
        article_page = urllib.request.urlopen(req)
        page_text = article_page.read()
    except Exception as e:
        page_text=""
        print(e)
    for token in referents:
        start = str(page_text).lower().find(token.lower())
        if start > 0:
            end = start + 800
            result = str(page_text)[start:end]
            referred = result.lower().find(contains)
            if not referred > 0:
                result = "not found in ack"
            break
    return result
    
# open articles csv file
catalysis_articles = {}
fieldnames=[]
input_file = 'ukch_pop_1refv.csv'
output_file = 'ukch_pop_1refv2.csv'
with open(input_file, newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         if fieldnames==[]:
             fieldnames=list(row.keys())
         if row['Include'] =='':
             print("Adding", row['Title'], row['DOI'])
             catalysis_articles[int(row['Num'])]=row
          
for cat_art_num in catalysis_articles.keys():
    if catalysis_articles[cat_art_num]['DOI'] != "":
        article_title = catalysis_articles[cat_art_num]['Title']
        doi_text = catalysis_articles[cat_art_num]['DOI']
        article_data = getCrossRefBibData(doi_text)
        if 'link' in article_data.keys():
            url = jsonToPlainText(article_data['link'])
            txt=findURIFrag(url,["acknowle"],"catalysis")
            print(cat_art_num,"|",url,"|", txt)
 


