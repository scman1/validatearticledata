import scholarly
import urllib.request
from difflib import SequenceMatcher
import csv
#from bs4 import BeautifulSoup


def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()


def findFromURI(name, uri, referents):
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
            end = start + 200
            result = str(page_text)[start:end]
            break
    return result


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

def findFromDOI(name, doi, referents):
    doi_url = 'https://dx.doi.org/'+ doi
    result = findFromURI(name, doi_url, referents)        
    return result


# open csv file
catalysis_articles = {}
input_file = 'ukch_pop_.csv'
output_file = 'ukch_pop_1ref.csv'
with open(input_file, newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         catalysis_articles[int(row['Num'])]=row
         
# for each entry
# get DOI and URI
for cat_art_num in catalysis_articles.keys():
    article_title = catalysis_articles[cat_art_num]['Title']
    article_doi   = catalysis_articles[cat_art_num]['DOI']
    article_url   = catalysis_articles[cat_art_num]['ArticleURL']
    print("Analysing:", cat_art_num, article_title, article_doi, article_url)
    # try to retrive html page for article using link from crossref first
    # and if not try url from pop
    # find reference to uk catalysis hub in html text
    # if found mark as relevant
    found = ""
    referents = ["uk catalysis hub", "uk catalysis", "catalysis hub"]
    found = findFromDOI(article_title, article_doi, referents)
    catalysis_articles[cat_art_num]['checked_doi'] = 1
    catalysis_articles[cat_art_num]['ack_ch'] = found
    if found == "" or found == None :
        found = findFromURI(article_title, article_url, referents)
        catalysis_articles[cat_art_num]['checked_url'] = 1     
        catalysis_articles[cat_art_num]['ack_ch'] = found


fieldnames = []
for cat_art_num in list(catalysis_articles.keys()):
	keys = list(catalysis_articles[cat_art_num].keys())
	for key in keys:
		if not key in fieldnames:
			fieldnames.append(key)

##########################################################
# test if direct dois have acknowledge section and if so,
# do they acknowledge UKCH
##########################################################
#for key in list(dois.keys()):
#    url = 'https://dx.doi.org/'+ dois[key]
#    txt=findURIFrag(url,["acknowle"],"catalysis")
#    print(key,"|", txt)

##########################################################
# test if direct url pages have acknowledge section and if so,
# do they acknowledge UKCH
##########################################################
#for key in list(urls.keys()):
#	txt=findURIFrag(urls[key],["acknowle"],"catalysis")
#	print(key,"|", txt)

#write back to a new csv file
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for cat_art_num in catalysis_articles.keys():
        writer.writerow(catalysis_articles[cat_art_num])


