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
        paras = soup.find_all('p')
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
                else:
                    likely = 0
    except Exception as e:
        page_text=""
        print(e)
    return result

# open csv file
catalysis_articles = {}
input_file = 'ukch_pop_1.csv'
output_file = 'ukch_pop_1refs.csv'
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
    if 'pdf' != article_url[len(article_url)-3:len(article_url)].lower():
        print("Analysing:", cat_art_num, article_title, article_doi, article_url)
        # try to retrive html page for article using link from crossref first
        # and if not try url from pop
        # find reference to funding or acknowledgement in html text
        # if found mark as relevant
        found = ""
        referents = ['funding', "thank", "acknowledge", "grant"]
        found = findFromURI(article_title, article_url, referents)
        catalysis_articles[cat_art_num]['checked_url'] = 1
        catalysis_articles[cat_art_num]['ack_ch'] = found
    else:
        print("Skip:", cat_art_num, article_title, article_doi, article_url)

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


