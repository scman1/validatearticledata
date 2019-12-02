import csv
from bs4 import BeautifulSoup

# open csv file
catalysis_articles = {}
input_file = 'ukch_pop_1refs.csv'
output_file = 'ukch_pop_1refc.csv'
with open(input_file, newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         catalysis_articles[int(row['Num'])]=row
         
# for each entry
# get DOI and URI
# Keywors for acknowlegement
referents = ['funding', "thank", "acknowledge", "grant"]
for cat_art_num in catalysis_articles.keys():
    catalysis_articles[cat_art_num]['ack_url'] = \
    BeautifulSoup(catalysis_articles[cat_art_num]['ack_url'],'html.parser').get_text() 
    catalysis_articles[cat_art_num]['ack_doi'] = \
    BeautifulSoup(catalysis_articles[cat_art_num]['ack_doi'],'html.parser').get_text() 
    
    
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


