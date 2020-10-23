from habanero import Crossref
from habanero import cn
import json

import lib.text_comp as txtc

cr = Crossref()

def getDOIForTitle(article_title):
    res = cr.works(query = article_title, select = ["DOI","title"])
    doi_text = ""
    max_similarity = 0
    closest_title = ""
    closest_doi = ""
    for recovered in res['message']['items']:
        if 'title' in recovered.keys():
            similarity = txtc.similar(recovered['title'][0], article_title)
            if similarity > 0.9:
                doi_text = recovered['DOI']
            else:
                if similarity > max_similarity:
                    max_similarty = similarity
                    closest_title = recovered['title'][0]
                    closest_doi = recovered['DOI']
##    if doi_text == "" :
##        print("closest match:", closest_title, "with DOI:", closest_doi)
##        print("use it?")
    return doi_text

def getBibData(doi_text):
    try:
        art_bib = json.loads(cn.content_negotiation(ids = doi_text, format = "citeproc-json"))
        return art_bib
    except:
        return {}

def getJSONFile(doi_text):
    try:
        art_bib = json.loads(cn.content_negotiation(ids = doi_text))
        return art_bib
    except:
        return {}