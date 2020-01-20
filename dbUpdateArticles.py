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
        print("Author Added", ins)

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

def get_author_id(fullname, givenname, lastname, ORCID = ""):
    id = -1
    db_author = con.execute(
        "SELECT * FROM Authors WHERE fullName='%s'" % fullname.replace("'","''")).fetchone( )
    #print("FULL MATCH",a_full, a_id, db_author)
    if not db_author is None:
        id = db_author[5]
    elif db_author is None and ORCID != '':
        db_author = con.execute(
            "SELECT * FROM Authors WHERE ORCID = '%s'" % ORCID).fetchone( )
        if not db_author is None:
            print("ORCID MATCH:", db_author, fullname, ORCID, db_author[3])
            id = db_author[5]  
    else:
    # try to match by last name using similarity
        db_authors = con.execute(
            "SELECT * FROM Authors WHERE LastName LIKE '"+"%"+ lastname.replace("'","''")+"%"+"'").fetchall( )
        if not db_authors is None:
            for db_author in db_authors:
                similarity = similar(fullname, db_author[0])
                if similarity > 0.8:
                    print("LASTNAME MATCH",fullname, lastname, db_author)
                    id = db_author[5]
                    break
            #inspect again to discard abreviations in names
            if id == -1:
                for db_author in db_authors:
                    id = db_author[5]
                    inspected = False
                    while not inspected:
                        print('***************************************************************')
                        print("Searching for:", fullname)
                        print("Found", db_author[0], "ID", db_author[5])
                        print('Options:')
                        print("a","-" , "Match found")
                        print("b","-" , "Continue Search")
                        print("Selection:")
                        usr_select = input()
                        if usr_select in ['a','b']:
                            if usr_select == "b":
                                id = -1
                            inspected = True
                    if id != -1:
                        break
                
    if id == -1:
        db_authors = con.execute(
            "SELECT * FROM Authors WHERE GivenName LIKE '"+"%"+ givenname.replace("'","''")+"%"+"'").fetchall( )
        if not db_authors is None:
            for db_author in db_authors:
                similarity = similar(fullname, db_author[0])
                if similarity > 0.8:
                    print("GIVENNAME MATCH",fullname, givenname, db_author)
                    id = db_author[5]
                    inspected = False
                    while not inspected:
                        print('***************************************************************')
                        print("Searching for:", fullname)
                        print("Found", db_author[0], "ID", db_author[5])
                        print('Options:')
                        print("a","-" , "Match found")
                        print("b","-" , "Continue Search")
                        print("Selection:")
                        usr_select = input()
                        if usr_select in ['a','b']:
                            if usr_select == "b":
                                id = -1
                            inspected = True
                if id != -1:
                    break
    return id


def add_new_articles(db_con, arts_file):
    # Update/Add articles verified by JG and CA
    catalysis_articles = {}
    fieldnames=[]
    with open(arts_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if fieldnames==[]:
                fieldnames=list(row.keys())
            catalysis_articles[int(row['NumUKCH'])]=row
        for new_art_id in catalysis_articles.keys():
            art_doi = catalysis_articles[new_art_id]['DOI']
            title = db_con.execute(
                 "SELECT title from Article_Updates where DOI='%s' and NumUKCH = '%s' " % (art_doi, new_art_id)).fetchone( )
            if str(type(title)) != "<class 'NoneType'>" and len(title) > 0:
                 print("Found:", new_art_id) #title[0])
                 u_action = catalysis_articles[new_art_id]['j_action']
                 ins = db_con.execute(
                     "UPDATE Article_Updates SET Action = '%s' WHERE DOI='%s' and NumUKCH = '%s'" % (u_action,art_doi, new_art_id)).fetchone( )
            else:
                print("Not Found:", art_doi)
                print("inserting")
                # build column list
                #columns = str(tuple(catalysis_articles[new_art_id].keys())).replace("'", "")
                #values = str(tuple(catalysis_articles[new_art_id].values()))
                #ins = db_con.execute(
                 #"UPDATE INTO Article_Updates SET Action = %s" % columns).fetchone( )
        db_con.commit()

def add_new_authors():
    # Select all authors from author update,
    # look up in article link
    # if article added then
    #    look up in authors,
    #    if found then get ID for creating Author-Article Link
    #    if not found then add author and create Author-Article Link
    #

    new_authors = \
                con.execute(
                    "SELECT AuthorNum, Name, LastName, fullName, ORCID from Author_Updates").fetchall( )

    i_found = 0
    i_not_found = 0
    for new_author in new_authors:
        # LookUp by ORCID
        author_ID = 0
        na_num, na_name, na_lastname, na_fullname, na_ORCID = new_author
        na_ORCID = new_author[4]
        na_fullname = new_author[3]
        na_name = new_author[1]
        na_lastname = new_author[2]
        na_num = new_author[0]
        # Lookup Authors and if needed add
        author_ID = get_author_id(na_fullname,na_name,na_lastname,na_ORCID)
        top_id = get_max_aut_id()
        if author_ID == -1:
            i_not_found += 1
            print("Not Found", i_not_found, new_author)
            top_id += 1
            author_ID = top_id
            # Need to add to the DB, before creating article-author-link
            new_author = {'FullName':na_fullname, "LastName":na_lastname, "GivenName":na_name, "ORCID":na_ORCID, "Articles":0, 'ID':author_ID}
            author_fields = ['FullName', "LastName", "GivenName", "ORCID", "Articles","ID"]
            add_authors(new_author, author_fields)
            print('ADDED AUTHOR:', author_ID)
        else:
            i_found += 1
            print("Found", i_found, new_author)
            # no need to add, just create article-author-link
        # create author link
        new_links = con.execute(
            "SELECT * FROM Article_Author_Link_Updates WHERE AuthorNum = '%s'" % (na_num)).fetchall( )
        for link in new_links:
                new_link = {'DOI':link[0], "AuthorNum":link[1], "mergedANum":author_ID,
                            "AuthorCount":link[7], "AuthorOrder":link[3], "UKCHNum":link[4],
                            'Action':link[6], "Sequence":link[5]}
                add_links(new_link)

def add_affiliation_author_link(db_con):
    # Lookup Affiliation link full name in authors table if found
    # just update the Author ID number
    # if not found look up last name
    # for each returned record
    #   - if records have orcid use it to try match
    #   - calculate the similarity of full names
    #   - if > 60 % ask if update

    affiliations = \
                db_con.execute(
                    "SELECT AffiLinkID, Name, LastName, FullName, ORCID from Affiliation_Links").fetchall( )
    i_found = 0
    i_not_found = 0
    for afi_author in affiliations:
        # LookUp by ORCID
        author_ID = 0
        afi_num, na_name, na_lastname, na_fullname, na_ORCID = afi_author
        # Lookup Author IDs
        author_ID = get_author_id(na_fullname,na_name,na_lastname,na_ORCID)
        if author_ID != -1:
            i_found += 1
            #print(na_fullname, "Found with ID:", author_ID)
        else:
            i_not_found += 1
            #print(na_fullname, "Not found")
        db_con.execute("UPDATE Affiliation_Links SET AuthorNum = '%s' WHERE AffiLinkID = '%s'" %(author_ID, afi_num)).fetchone( )
    db_con.commit()
    print("Found:", i_found, "Not Found:", i_not_found)
    
dbname = 'ukch_articles.sqlite'
db_con = sqlite.connect(dbname)
art_doi = "10.1038/s41929-019-0334-3"
title = db_con.execute(
    "SELECT title from Articles where DOI='%s'" % art_doi).fetchone( )

# open update actions file
arts_file = 'NewBibUKCHCAJGEdit.csv'




#add_new_articles(db_con, arts_file)
#add_new_authors()
#add_affiliation_author_link(db_con)

#verify addresses

# Lookup Affiliation link affiliations and affiliation address
# 
# just update the Author ID number
    # if not found look up last name
    # for each returned record
    #   - if records have orcid use it to try match
    #   - calculate the similarity of full names
    #   - if > 60 % ask if update

affiliations = \
                db_con.execute(
                    "SELECT AffiLinkID, UniqueID, affiliations from Affiliation_Links").fetchall( )
i_found = 0
i_not_found = 0
for affi_record in affiliations:
    #get the corresponding address record and check if addresses match
    affiLinkID, Affiliation_ID, affiliation_text = affi_record
    affi_addresses = \
                db_con.execute(
                    "SELECT * from Affiliation_Addresses WHERE AffiLinkID = '%s'"% (affiLinkID)).fetchall( )
    if not affi_addresses is None:
        addr_occurrences = 0
        for field in affi_addresses[0]:
            #print(field,affiliation_text)
            if field in affiliation_text:
                addr_occurrences += 1
        if addr_occurrences == 0:
            print("ADDRESS:", affiLinkID, Affiliation_ID, affi_addresses, "match not found in:", affiliation_text)

    #get the affiliation record and check if institutions match
    an_affiliation = \
                db_con.execute(
                    "SELECT Institution, Country from Affiliations WHERE ID = '%s'"% (Affiliation_ID)).fetchall( )
   
    if not an_affiliation is None:
        inst_occurrences = 0
        for field in an_affiliation[0]:
            #print(field,affiliation_text)
            if field in affiliation_text:
                inst_occurrences += 1
        if inst_occurrences == 0:
            print("INSTITUTION:", affiLinkID, Affiliation_ID, an_affiliation, "match not found in:", affiliation_text)
