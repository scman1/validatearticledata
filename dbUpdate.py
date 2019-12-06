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

def add_authors(author, fieldnames):
        aut_id = author['ID']
        print("adding:", aut_id)
        # build column list
        columns = str(tuple(author.keys())).replace("'", "")
        values = str(tuple(author.values()))
        ins = con.execute(
            "INSERT INTO Authors %s VALUES  %s " % (columns, values)).fetchone( )
        con.commit()

def add_links(art_aut_link):
    art_doi = art_aut_link['DOI']
    aut_id = art_aut_link['mergedANum']
    link_doi = con.execute(
         "SELECT DOI from Article_Author_Link where DOI='%s' and mergedANum = '%s'" % (art_doi, aut_id)).fetchone( )
    if str(type(link_doi)) != "<class 'NoneType'>" and len(link_doi) > 0:
         print("Found:", link_doi[0])
    else:
        print("Not Found:", art_doi, "inserting", art_aut_link)
        # build column list
        columns = str(tuple(art_aut_link.keys())).replace("'", "")
        values = str(tuple(art_aut_link.values()))
        ins = con.execute(
            "INSERT INTO Article_Author_Link %s VALUES  %s " % (columns, values)).fetchone( )
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
author_records, author_fields = get_data(auts_file, 'ID')


links_file = 'UKCCHArtAutLinkAdded201911Load.csv'
links_records, links_fields = get_data(links_file, 'ID')

top_id = get_max_aut_id()
new_id = 0

for key in author_records.keys():
    a_row = author_records[key]
    a_full = a_row['FullName']
    a_last = a_row['LastName']
    a_given = a_row['GivenName']
    a_id = a_row['ID']
    db_id = get_author_id(a_full,a_given, a_last)
    if db_id == -1:
        top_id += 1
        new_id = top_id
        a_row['ID'] = new_id
        print("no match found add as new", a_full, "new ID:",top_id)
        add_authors(a_row, links_fields)
    else:
        print("match found only add art_aut_link id:", db_id)
        new_id = db_id
    for key in links_records.keys():
        a_num = links_records[key]['mergedANum']
        row = links_records[key]
        if a_num == a_id:
            if 'ID' in links_fields:
                row.pop('ID')
            row['mergedANum'] = new_id
            add_links(row)
###############################################################################
# authors/articles link file
###############################################################################


###############################################################################
# authors file
###############################################################################


