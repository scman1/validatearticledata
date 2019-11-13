#read csvfile
import csv
##with open('UKCatalysisHubArticles201910.csv', newline='') as csvfile:
##     spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
##     for row in spamreader:
##         print(', '.join(row))

# open articles csv file
catalysis_articles = {}
fieldnames=[]
with open('UKCatalysisHubArticles201910Mod.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         catalysis_articles[int(row['Num'])]=row
         fieldnames=row.keys()
         if row['Identifier'] == "":
            print(row['Title'], row['Identifier'])

#fill in the missing identifier with a message
for cat_art_num in catalysis_articles.keys():
    if catalysis_articles[cat_art_num]['Identifier'] =="":
        catalysis_articles[cat_art_num]['Identifier'] = "missing"
        
#write back to a new csv file
with open('UKCatalysisHubArticles201910Rev.csv', 'w', newline='') as csvfile:
    #fieldnames = ['Num', 'Phase', 'P', 'CatalysisTheme', 'ProjectYear', 'Authors', 'Title', 'Journal', 'PublicationDate', 'Identifier']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for cat_art_num in catalysis_articles.keys():
        writer.writerow(catalysis_articles[cat_art_num])
