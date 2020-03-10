from habanero import Crossref
from difflib import SequenceMatcher
import re

def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()

cr = Crossref()


def getArticleDOIFromCrossref(article_title):
    res = cr.works(query = article_title, select = ["DOI","title"])
    doi_text=""
    for recovered in res['message']['items']:
        similarity = similar(recovered['title'][0], article_title)
        #print(recovered['title'][0], similarity)
        if similarity > 0.9:
            doi_text = recovered['DOI']
    return doi_text


article_title = 'Waste not want not CO2 re cycling into block polymers'

##doi_text = ""
##res = cr.works(query = article_title, select = ["DOI","title"])
##
##
##for recovered in res['message']['items']:
##    similarity = similar(recovered['title'][0], article_title)
##    print(recovered['title'][0], similarity)
##    if similarity > 0.9:
##        doi_text = recovered['DOI']

doi_text=getArticleDOIFromCrossref(article_title)

print(doi_text)

