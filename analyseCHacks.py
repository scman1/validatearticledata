import csv
from bs4 import BeautifulSoup

def lookupKeywords(sentence, keywords):
    # The tokens for the acknowledge statement are taken from
    # phase 1 = "UK Catalysis Hub is kindly thanked for resources and support
    #            provided via our membership of the UK Catalysis Hub Consortium
    #            and funded by EPSRC grant: EP/K014706/2, EP/K014668/1,
    #            EP/K014854/1, EP/K014714/1 or EP/M013219/1"    
    # phase 2 = "UK Catalysis Hub is kindly thanked for resources and support
    #            provided via our membership of the UK Catalysis Hub Consortium
    #            and funded by EPSRC grant:  EP/R026939/1, EP/R026815/1,
    #            EP/R026645/1, EP/R027129/1 or EP/M013219/1 biocatalysis"

    value = 0
    for token in keywords:
        if token in sentence:
            value += 1
    return value
    
        

# open csv file
catalysis_articles = {}
input_file = 'ukch_pop_1refc.csv'
output_file = 'ukch_pop_1refd.csv'
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
            'thanked', 'EP/K014854/1', 'EP/K014706/2']

for cat_art_num in catalysis_articles.keys():
    ack_url = catalysis_articles[cat_art_num]['ack_url']
    if ack_url != "":
        catalysis_articles[cat_art_num]['ack_url_val'] = lookupKeywords(ack_url, keywords)    
    ack_doi = catalysis_articles[cat_art_num]['ack_doi']
    if ack_doi != "":
        catalysis_articles[cat_art_num]['ack_doi_val'] = lookupKeywords(ack_doi, keywords)
    
    
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


