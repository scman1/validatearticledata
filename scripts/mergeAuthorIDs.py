from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()



# Use content to retrieve article data by DOI
# would be better to use json but somehow it is slower than bibentry+RIS
def getCrossRefBibData(doi_text):
    try:
        art_bib = json.loads(cn.content_negotiation(ids = doi_text, format = "citeproc-json"))
        return art_bib
    except:
        return {}

def jsonToPlainText(element):
    if isinstance(element, int) or \
       isinstance(element, float) or \
       isinstance(element, str):
        return element
    elif 'date-parts' in element:
        return element['date-parts'][0]
    elif 'issue' in element:
        return element['issue']
    elif isinstance(element, list) \
         and len(element) > 0 and 'URL' in element[0]:
        return element[0]['URL']
    

###########################################################################################
# open articles csv files
catalysis_articles = {}
fieldnames=[]
with open('UKCatalysisHubArticles201910VerCN.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         if fieldnames==[]:
             fieldnames=list(row.keys())
         catalysis_articles[int(row['Num'])]=row
         
fieldnames.append('similarity')
fieldnames.append('CRTitle')

cr_articles = {}
article_columns=[]

with open('UKCCHArticles201910CR.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         if article_columns==[]:
             article_columns=list(row.keys())
         cr_articles[int(row['NumUKCH'])]=row

for cat_art_num in cr_articles.keys():
    ch_title = catalysis_articles[cat_art_num]['Title']
    cr_title = cr_articles[cat_art_num]['title']
    similarity = similar(ch_title,cr_title)
    catalysis_articles[cat_art_num]['similarity'] = similarity
    catalysis_articles[cat_art_num]['CRTitle'] = cr_title
    
# write back to a new csv file
# create three files

with open('UKCatalysisHubArticles201910VerTitles.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()
    for cat_art_num in catalysis_articles.keys():
        writer.writerow(catalysis_articles[cat_art_num])
