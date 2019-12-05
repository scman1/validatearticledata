import csv
import string
from sqlite3 import dbapi2 as sqlite
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()

def add_articles(input_file):
    catalysis_articles = {}
    fieldnames=[]
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if fieldnames==[]:
                fieldnames=list(row.keys())
            catalysis_articles[int(row['NumUKCH'])]=row
        for new_art_id in catalysis_articles.keys():
            art_doi = catalysis_articles[new_art_id]['DOI']
            title = con.execute(
                 "SELECT title from Articles where DOI='%s'" % art_doi).fetchone( )
            if str(type(title)) != "<class 'NoneType'>" and len(title) > 0:
                 print("Found:", title[0])
            else:
                print("Not Found:", art_doi)
                print("inserting")
                # build column list
                columns = str(tuple(catalysis_articles[new_art_id].keys())).replace("'", "")
                values = str(tuple(catalysis_articles[new_art_id].values()))
                ins = con.execute(
                 "INSERT INTO Articles %s VALUES  %s " % (columns, values)).fetchone( )
        con.commit()

def get_data(input_file, id_field):
    csv_data = {}
    fieldnames=[]
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if fieldnames==[]:
                fieldnames=list(row.keys())
            csv_data[int(row[id_field])]=row
    return csv_data, fieldnames

def get_max_aut_id():
    db_author = con.execute("SELECT MAX(ID) FROM Authors").fetchone( )
    return db_author[0]

def get_author_id(fullname,givenname, lastname):
    id = -1
    db_author = con.execute(
        "SELECT * FROM Authors WHERE FullName='%s'" % fullname.replace("'","''")).fetchone( )
    #print("FULL MATCH",a_full, a_id, db_author)
    if not db_author is None:
        id = db_author[5]
    elif db_author is None:
    # try to match by last name using similarity
        db_authors = con.execute(
            "SELECT * FROM Authors WHERE fullName LIKE '"+"%"+ lastname.replace("'","''")+"%"+"'").fetchall( )
        if not db_authors is None:
            for db_author in db_authors:
                similarity = similar(fullname, db_author[0])
                if similarity > 0.8:
                    print("LASTNAME MATCH",a_full, a_id, db_author[5])
                    id = db_author[5]
                    break
    if id == -1:
        db_authors = con.execute(
            "SELECT * FROM Authors WHERE fullName LIKE '"+"%"+ givenname.replace("'","''")+"%"+"'").fetchall( )
        if not db_authors is None:
            for db_author in db_authors:
                similarity = similar(fullname, db_author[0])
                if similarity > 0.8:
                    print("GIVENNAME MATCH",a_full, a_id, db_author[5])
                    id = db_author[5]
                    break
    return id
                
    


dbname = 'ukch_articles.sqlite'
con = sqlite.connect(dbname)
art_doi = "10.1038/s41929-019-0334-3"
title = con.execute(
    "SELECT title from Articles where DOI='%s'" % art_doi).fetchone( )

# open csv file and read new articles
# look up the doi of each new article and if it does not exist add it to the DB

###############################################################################
# articles csv file
###############################################################################
arts_file = 'UKCCHArticlesAdded201911.csv'
# add_articles(arts_file)

# New articles have action null while authors and author_article_links
# are pending
auts_file = 'UKCCHAuthorsAdded201911Load.csv'
author_records, author_fields = get_data(auts_file, 'mergeANum')

top_id = get_max_aut_id()

for key in  author_records.keys():
    a_full = author_records[key]['FullName']
    a_last = author_records[key]['LastName']
    a_given = author_records[key]['GivenName']
    a_id = author_records[key]['mergeANum']
    db_id = get_author_id(a_full,a_given, a_last)
    if db_id == -1:
        top_id += 1
        print("no match found add as new", a_full, "new ID:",top_id)
        #with corresponding art_aut_link
    else:
        print("match found only add art_aut_link id:", db_id) 


###############################################################################
# authors/articles link file
###############################################################################


###############################################################################
# authors file
###############################################################################


