import scholarly
import urllib
from difflib import SequenceMatcher
import re
#from bs4 import BeautifulSoup


def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()



article_title = 'The adsorption of Cu on the CeO2(110) surface'
search_query = scholarly.search_pubs_query(article_title)

link = ""
while True:
    try:
        pub = next(search_query).fill()
        print(pub)
        recovered = pub.bib['title']
        if similar(recovered, article_title) > 0.8:
            link = pub.bib['url']
            break
        else:
            print("not matching", recovered)
    except:
       break

if link != "":
    article_page = urllib.request.urlopen(link)
    page_text = article_page.read()
    #print(page_text)
    #parsed_html = BeautifulSoup(page_text)
    start = str(page_text).find("DOI:") + 4
    end = start + 80
    substr = str(page_text)[start:end]
    doi_list = re.findall(r"^10.\d{4,9}/[-._;()/:A-Z0-9]+",substr)
    if len(doi_list) > 0:
        result = doi_list[0]
        print(result)

