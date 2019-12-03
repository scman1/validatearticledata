from habanero import Crossref
from difflib import SequenceMatcher
import re
import csv

def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()

cr = Crossref()


def getArticleDOIFromCrossref(article_title):
    doi_text=""
    try:
        res = cr.works(query = article_title, select = ["DOI","title"])
        for recovered in res['message']['items']:
            similarity = similar(recovered['title'][0], article_title)
            #print(recovered['title'][0], similarity)
            if similarity > 0.9:
                doi_text = recovered['DOI']
    except:
        doi_text=""
    return doi_text

# working with csv data files
catalysis_articles = {}
input_file = 'UKCH201911c.csv'
output_file = 'UKCH201911cDOI.csv'
# open input csv file
with open(input_file, newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         catalysis_articles[int(row['CatArtNum'])]=row
         
#fill in the missing identifier
for cat_art_num in catalysis_articles.keys():
    article_title = catalysis_articles[cat_art_num]['Title']
    doi_text=getArticleDOIFromCrossref(article_title)
    catalysis_articles[cat_art_num]['DOICR'] = doi_text
    catalysis_articles[cat_art_num]['checked'] = 1
    print(cat_art_num, article_title)
    

fieldnames = []
for cat_art_num in list(catalysis_articles.keys()):
	keys = list(catalysis_articles[cat_art_num].keys())
	for key in keys:
		if not key in fieldnames:
			fieldnames.append(key)


    
#write back to a new csv file
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for cat_art_num in catalysis_articles.keys():
        writer.writerow(catalysis_articles[cat_art_num])
