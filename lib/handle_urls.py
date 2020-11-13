import requests
import urllib
from bs4 import BeautifulSoup

def findFromURI(name, uri, referents):
    result = ""
    try:
        req_head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        response = requests.get(uri, headers = req_head)
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

def getPageFromDOI (doi):
    doi_url = 'https://dx.doi.org/'+ doi
    page_text = ""
    try:
        req = urllib.request.Request(doi_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
        article_page = urllib.request.urlopen(req)
        page_text = article_page.read()
    except Exception as e:
        print(e)
    return page_text

def getPageFromURL(url_text):
    page_text = ""
    try:
        req_head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        response = requests.get(url_text, headers = req_head)
        page_text = response.text
    except Exception as e:
        print(e)
    return page_text

def getPageHeader(url_text):
    response = None
    try:
        req_head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        response = requests.head(url_text, headers = req_head)
    except Exception as e:
        print(e)
    return response


