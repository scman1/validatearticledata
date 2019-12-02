#
# Get list of Catalysis Hub in Articles acknowledged
# in Website
#

import csv
import requests
from bs4 import BeautifulSoup

def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()

def getHTMLPage(url):
    soup = None
    try:
        req_head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        response = requests.get(url, headers = req_head)
        soup = BeautifulSoup(response.text,'html.parser')
    except Exception as e:
        print(e)
    return soup


def getLinks(soup):
    result = []
    try:
        for link in soup.find_all('a'):
            result.append(link.get('href'))
    except Exception as e:
        print(e)
    return result

def getParagraphs(soup):
    result = []
    try:
        for para in soup.find_all('p'):
            result.append(para)
    except Exception as e:
        print(e)
    return result


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


# Read the publications page from UKCH and get a list of articles
pub_urls = ['https://ukcatalysishub.co.uk/publications', 'https://ukcatalysishub.co.uk/biocatalysis-publications-2017/', 'https://ukcatalysishub.co.uk/design-publications-2013/', 'https://ukcatalysishub.co.uk/design-publications-2014/', 'https://ukcatalysishub.co.uk/design-publications-2015/', 'https://ukcatalysishub.co.uk/design-publications-2016/', 'https://ukcatalysishub.co.uk/design-publications-2017/', 'https://ukcatalysishub.co.uk/energy-publications-2014/', 'https://ukcatalysishub.co.uk/energy-publications-2015/', 'https://ukcatalysishub.co.uk/energy-publications-2016/', 'https://ukcatalysishub.co.uk/energy-publications-2017/', 'https://ukcatalysishub.co.uk/environment-publications-2014/', 'https://ukcatalysishub.co.uk/environment-publications-2015/', 'https://ukcatalysishub.co.uk/environment-publications-2016/', 'https://ukcatalysishub.co.uk/environment-publications-2017/', 'https://ukcatalysishub.co.uk/transformations-publications-2014/', 'https://ukcatalysishub.co.uk/transformations-publications-2015/', 'https://ukcatalysishub.co.uk/transformations-publications-2016/', 'https://ukcatalysishub.co.uk/transformations-publications-2017/']


output_file = 'UKCH201911f.csv'


catalysis_articles = {}
single_article = {}
i = 0
for pub_url in pub_urls:
    parsed_page = getHTMLPage(pub_url)
    list_of_links = getLinks(parsed_page)
    list_of_paragraphs = getParagraphs(parsed_page)
    for para in list_of_paragraphs:
        authors = title = pub_data = link_text = art_ref = ""
        single_article={}
        if para.find('strong') and para.find('a'):
            # standard formating until 2018 on landing page
            i += 1
            full_para = para.get_text()
            title = para.find('strong').get_text()
            start_title = full_para.index(title)
            end_title = start_title + len(title) 
            authors = full_para[0:start_title-2]
            link_text = para.find('a').get_text()
            art_ref= para.find('a').get('href')
            start_link =  full_para.index(link_text)
            pub_data = full_para[end_title+2:start_link-2]
            single_article['CatArtNum'] = i
            single_article['Authors'] = authors
            single_article['Title'] = title
            single_article['PubData'] = pub_data
            single_article['LinkText'] = link_text
            single_article['ArtRef'] = art_ref
            catalysis_articles[i] = single_article
        elif para.find('strong') and i > 80:
            # non standard formating, title but no link
            i += 1
            full_para = para.get_text()
            title = para.find('strong').get_text()
            start_title = full_para.index(title)
            end_title = start_title + len(title) 
            authors = full_para[0:start_title-2]
            pub_data = full_para[end_title+2:len(full_para)]
            single_article['CatArtNum'] = i
            single_article['Authors'] = authors
            single_article['Title'] = title
            single_article['PubData'] = pub_data
            single_article['LinkText'] = link_text
            single_article['ArtRef'] = art_ref
            catalysis_articles[i] = single_article
        elif i >= 102:
            i += 1
            #get non formated on main page (will bring some trash)
            single_article['CatArtNum'] = i
            single_article['blob'] = para.get_text()
            catalysis_articles[i] = single_article

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



