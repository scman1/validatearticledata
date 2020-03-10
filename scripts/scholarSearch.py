import scholarly
import urllib
from difflib import SequenceMatcher
import re
import csv
#from bs4 import BeautifulSoup


def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()


search_string = 'UK Catalysis Hub'
search_query = scholarly.search_pubs_query(search_string)

articles_list = {}
fieldnames = ["Num"]
i = 0

while True:
    try:
        pub = next(search_query).fill()
        keys = list(pub.bib.keys())
        i+=1
        row={}
        row["Num"] =  i
        for key in keys:
            if not key in fieldnames:
                fieldnames.append(key)
            row[key] = pub.bib[key]
        articles_list[i] = row   
    except:
       break



#write results to a csv file
with open('scholarResults.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for cat_art_num in articles_list.keys():
        writer.writerow(articles_list[cat_art_num])
