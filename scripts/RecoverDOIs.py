import scholarly
import urllib
from difflib import SequenceMatcher
import re
#from bs4 import BeautifulSoup


def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()


article_title = 'Waste not, want not: CO2 (re)cycling into block polymers'
search_query = scholarly.search_pubs_query(article_title)

link = ""
while True:
    try:
        pub = next(search_query).fill()
        recovered = pub.bib['title']
        if similar(recovered, article_title) > 0.8:
            link = pub.bib['url']
            break
        else:
            print("not matching", recovered)
    except:
       break

page_text=""
result = ""

if link != "":
    try:
        req = urllib.request.Request(link)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
        article_page = urllib.request.urlopen(req)
        page_text = article_page.read()
    except Exception as e:
        page_text=""
        print(e)
    #print(page_text)
    #parsed_html = BeautifulSoup(page_text)
    start = str(page_text).find("DOI:") + 4
    end = start + 80
    substr = str(page_text)[start:end]
    doi_list = re.findall(r"^10.\d{4,9}/[-._;()/:A-Z0-9]+",substr)
    if len(doi_list) > 0:
        result = doi_list[0]
        print(result)


doi_url = 'https://dx.doi.org/'+ result
req = urllib.request.Request(doi_url)
req.add_header('Accept', 'text/bibliography; style=bibtex')
doi_page = urllib.request.urlopen(req)
doi_text = doi_page.read()

