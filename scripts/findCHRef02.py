#
# Find references/acknowledgement to Catalysis Hub in Articles
#

import csv
import requests
from bs4 import BeautifulSoup

def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()

def findFromURI(name, url, referents):
    result = ""
    try:
        req_head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        response = requests.get(url, headers = req_head)
        soup = BeautifulSoup(response.text,'html.parser')
        paras = soup.find_all('span')
        heywords=referents
        best_match = likely = 0
        for para in paras:
            for keyword in heywords:
                if keyword in str(para).lower():
                    likely += 1
            if likely > 0:
                if result == "" or likely > best_match:
                    result = str(para)
                    best_match = likely
                    likely = 0
                elif likely == best_match:
                    result = result + "\n" + str(para)
                    best_match = likely
                    likely = 0
                else:
                    likely = 0
    except Exception as e:
        print(e)
    return result

def findFromDOI(name, doi, referents):
    doi_url = 'https://dx.doi.org/'+ doi
    result = findFromURI(name, doi_url, referents)        
    return result


# open csv file
catalysis_articles = {}
input_file = 'UKCHpopBatch01Candidates.csv'
output_file = 'UKCHpopBatch01CandidatesR.csv'
with open(input_file, newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         catalysis_articles[int(row['Num'])]=row
         
# for each entry
# get DOI and URI
# Keywors for acknowlegement
keywords = ['EP/R026645/1', 'resources', 'EP/K014668/1', 'EPSRC', 'EP/K014714/1',
            'Hub', 'provided', 'grant', 'biocatalysis', 'EP/R026815/1',
            'EP/R026939/1', 'support', 'membership', 'EP/M013219/1', 'UK',
            'kindly', 'Catalysis', 'funded', 'EP/R027129/1', 'Consortium',
            'thanked', 'EP/K014854/1', 'EP/K014706/2', 'funding', "thank",
            "acknowledge"]

for cat_art_num in catalysis_articles.keys():
    article_title = catalysis_articles[cat_art_num]['Title']
    article_doi   = catalysis_articles[cat_art_num]['DOI']
    article_url   = catalysis_articles[cat_art_num]['ArticleURL']
    if catalysis_articles[cat_art_num]['acknowledgement']=="":
        print("URL:", cat_art_num, article_url)
        # try to retrive html page for article using link from crossref first
        # and if not try url from pop
        # find reference to funding or acknowledgement in html text
        # if found mark as relevant
        found = ""
        found = findFromURI(article_title, article_url, keywords)
        catalysis_articles[cat_art_num]['checked_url'] = 1
        catalysis_articles[cat_art_num]['ack_url'] = found
        if article_doi != "":
            print("DOI:", cat_art_num, article_doi)
            # try to retrive html page for article using link from crossref first
            # and if not try url from pop
            # find reference to funding or acknowledgement in html text
            # if found mark as relevant
            found = ""
            found = findFromDOI(article_title, article_doi, keywords)
            catalysis_articles[cat_art_num]['checked_doi'] = 1
            catalysis_articles[cat_art_num]['ack_doi'] = found

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


