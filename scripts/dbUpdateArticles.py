import csv
import string
from sqlite3 import dbapi2 as sqlite
from difflib import SequenceMatcher
import requests
from bs4 import BeautifulSoup

from habanero import Crossref
from habanero import cn
import json

cr = Crossref()

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

def verify_addresses(db_con):
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

# Read the publications page from UKCH and get a list of articles
pub_urls = ['https://ukcatalysishub.co.uk/publications', 'https://ukcatalysishub.co.uk/biocatalysis-publications-2017/',
            'https://ukcatalysishub.co.uk/design-publications-2013/', 'https://ukcatalysishub.co.uk/design-publications-2014/',
            'https://ukcatalysishub.co.uk/design-publications-2015/', 'https://ukcatalysishub.co.uk/design-publications-2016/',
            'https://ukcatalysishub.co.uk/design-publications-2017/', 'https://ukcatalysishub.co.uk/energy-publications-2014/',
            'https://ukcatalysishub.co.uk/energy-publications-2015/', 'https://ukcatalysishub.co.uk/energy-publications-2016/',
            'https://ukcatalysishub.co.uk/energy-publications-2017/', 'https://ukcatalysishub.co.uk/environment-publications-2014/',
            'https://ukcatalysishub.co.uk/environment-publications-2015/', 'https://ukcatalysishub.co.uk/environment-publications-2016/',
            'https://ukcatalysishub.co.uk/environment-publications-2017/', 'https://ukcatalysishub.co.uk/transformations-publications-2014/',
            'https://ukcatalysishub.co.uk/transformations-publications-2015/', 'https://ukcatalysishub.co.uk/transformations-publications-2016/',
            'https://ukcatalysishub.co.uk/transformations-publications-2017/']

def insert_record(db_con, new_record, table):
    # build column list
    columns = str(tuple(new_record.keys())).replace("'", "")
    values = str(tuple(new_record.values()))
    ins = db_con.execute(
            "INSERT INTO %s %s VALUES  %s " % (table, columns, values)).fetchone( )
    db_con.commit()


def verify_themes(db_con):
    article_list = db_con.execute(
                        "SELECT articles.doi, articles.title, articles.pub_print_year, articles.pub_ol_year, articles.id, article_theme_links.theme_id "+
                        "  FROM articles LEFT JOIN article_theme_links " +
                        "    ON LOWER(articles.doi) = LOWER(article_theme_links.doi) " +
                        "  WHERE article_theme_links.theme_id is null AND articles.action <> 'Remove'").fetchall( )
    theme_list = db_con.execute(
                        "SELECT themes.id, themes.short "+
                        "  FROM themes ").fetchall( )
    if not article_list is None:
        art_count = len(article_list)
        for article in article_list:
            doi = article[0]
            title = article[1]
            skip = len(theme_list) + 1
            print("Title:", article[1], "Print:", article[2], "On-Line:", article[3])
            inspected = False
            while not inspected:
                print('***************************************************************')
                print("Searching for:", doi)
                print("Found", article[0], "ID", "Print:", article[2], "On-Line:", article[3])
                print('Options:')
                for theme in theme_list:
                    print(theme[0], "-" , theme[1])
                print(skip,"-" , "Skip")
                print("Selection:") 
                usr_select = int(input())
                if usr_select in range(1, skip):
                    if usr_select != skip:
                        print(theme_list[usr_select-1], "\n Year:")
                        year_select = int(input())
                        print("Project:")
                        project_select = input()
                        new_theme_link={'id':0, 'doi':article[0], 'project':project_select,
                                         'theme_id':usr_select, 'project_year':year_select,
                                         'article_id':article[4]}
                        insert_record(db_con, new_theme_link, 'article_theme_links')
                    
                    inspected = True
                    print(inspected)
                    if inspected:
                        print("inspected")

        print ("Unclassified articles:", art_count)


def check_articles_db(db_con, in_file, out_file):
    # check if articles are already in DB
    catalysis_articles = {}
    fieldnames=[]
    i_found = 0
    i_not_found = 0
    with open(in_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if fieldnames==[]:
                fieldnames=list(row.keys())
            catalysis_articles[int(row['CatArtNum'])]=row
        article_list = db_con.execute(
                        "SELECT articles.doi, articles.title "+
                        "  FROM articles WHERE articles.action <> 'Remove'").fetchall( )
        # first pass by title
        for new_art_id in catalysis_articles.keys():
            art_title = catalysis_articles[new_art_id]['Title']
            catalysis_articles[new_art_id]["Registered"] = 0
            catalysis_articles[new_art_id]["Similarity"] = 0
            art_doi = db_con.execute(
                 "SELECT DOI from Articles where Title LIKE '%s' " % (art_title)).fetchone( )
            if str(type(art_doi)) != "<class 'NoneType'>" and len(art_doi) > 0:
                 print("Found:", art_title, art_doi) #title[0])
                 catalysis_articles[new_art_id]["Registered"] = 1
                 catalysis_articles[new_art_id]["Similarity"] = 1
                 catalysis_articles[new_art_id]["DOI"] = art_doi
                 i_found += 1
            else:
                # second pass look up similarity
                for article in article_list:
                    db_title = article[1]
                    similarity = similar (db_title.lower(), art_title.lower())
                    
                    if similarity > 0.8:
                        i_found += 1
                        # almost positive match
                        if catalysis_articles[new_art_id]["Similarity"] < similarity:
                            catalysis_articles[new_art_id]["Registered"] = 2
                            catalysis_articles[new_art_id]["DOI"] = article[0]
                            catalysis_articles[new_art_id]["Similarity"] = similarity
                    elif similarity > 0.5:    
                        # verify match
                        i_found += 1
                        if catalysis_articles[new_art_id]["Similarity"] < similarity:
                            catalysis_articles[new_art_id]["Registered"] = 3
                            catalysis_articles[new_art_id]["DOI"] = article[0]
                            catalysis_articles[new_art_id]["Similarity"] = similarity
            if catalysis_articles[new_art_id]["Registered"] == 0:
                print("Not Found:", art_doi)
                i_not_found += 1        
        
    print("Registered", i_found,"Not Registered", i_not_found)
    fieldnames.append("Registered")
    fieldnames.append("Similarity")
    fieldnames.append("DOI")
    
    #write back to a new csv file
    with open(out_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for cat_art_num in catalysis_articles.keys():
            writer.writerow(catalysis_articles[cat_art_num])

def get_articles_doi(in_file, out_file):
    # check if articles are already in DB
    catalysis_articles = {}
    fieldnames=[]
    i_found = 0
    i_not_found = 0
    with open(in_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if fieldnames==[]:
                fieldnames=list(row.keys())
            if row['Action'] == 'Add':
                catalysis_articles[int(row['CatArtNum'])]=row
        for new_art_id in catalysis_articles.keys():
            art_title = catalysis_articles[new_art_id]['Title']
            art_doi = catalysis_articles[new_art_id]['DOI']
            cr_doi = getArticleDOIFromCrossref(art_title)
            if cr_doi != art_doi:
                print("Found:", cr_doi, "for", art_title)
                catalysis_articles[new_art_id]['crDOI'] = cr_doi
                i_found+=1
            else:
                catalysis_articles[new_art_id]['crDOI'] = cr_doi 
                i_not_found += 1    
            
    print("Found", i_found,"Not Found", i_not_found)
    fieldnames.append("crDOI")
    
    #write back to a new csv file
    with open(out_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for cat_art_num in catalysis_articles.keys():
            writer.writerow(catalysis_articles[cat_art_num])

def verify_articles_doi(in_file, out_file):
    # check if articles are already in DB
    catalysis_articles = {}
    fieldnames=[]
    with open(in_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if fieldnames==[]:
                fieldnames=list(row.keys())
            catalysis_articles[int(row['CatArtNum'])]=row
            
        for new_art_id in catalysis_articles.keys():
            if catalysis_articles[new_art_id]['Action'] == 'Add':
                art_title = catalysis_articles[new_art_id]['Title']
                art_doi = catalysis_articles[new_art_id]['crDOI']
                result = verifyArticleDOIinCrossrefCN(art_title,art_doi)
                catalysis_articles[new_art_id]['DOIOK'] = result[0]
                print(result)

    fieldnames.append("DOIOK")
    
    #write back to a new csv file
    with open(out_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for cat_art_num in catalysis_articles.keys():
            writer.writerow(catalysis_articles[cat_art_num])

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

def getArticleDOIFromCrossref(article_title):
    res = cr.works(query = article_title, select = ["DOI","title"])
    doi_text=""
    for recovered in res['message']['items']:
        if 'title' in recovered.keys() and 'DOI' in recovered.keys():
            similarity = similar(recovered['title'][0].lower(), article_title.lower())
            #print(recovered['title'][0], similarity)
            if similarity > 0.7:
                doi_text = recovered['DOI']
    return doi_text

#use content to find articles by key
def verifyArticleDOIinCrossrefCN(article_title,doi_text):
    article_data = getCrossRefBibData(doi_text)
    cr_title = cr_doi = ""
    doi_match = False
    similarity = 0    
    if not article_data == {}:
        cr_title = jsonToPlainText(article_data['title'])
        cr_doi = jsonToPlainText(article_data['DOI'])
        similarity = similar(cr_title.lower(), article_title.lower())
        if similarity > 0.7:
            doi_match=True
        else:
            print("Difference|",similarity, "|", article_title, "|", doi_text, "|", cr_title, "|", cr_doi)
    return [doi_match, cr_title, cr_doi, similarity]

def verifyArticleDOIinCrossref(article_title,doi_text):
    res = cr.works(query = doi_text, select = ["DOI","title"])
    doi_match=False
    try:
        for recovered in res['message']['items']:
            similarity = similar(recovered['title'][0].lower(), article_title.lower())
            #print(recovered['title'][0], similarity)
            if similarity > 0.9:
                doi_match=True
                break
            else:
                print("Difference",similarity, article_title, recovered['title'][0])
    except:
        doi_match=False
    return doi_match

def buildDBfromJSON(input_file):
    catalysis_articles = {}
    fieldnames=[]
    with open(input_file, newline='') as csvfile:
         reader = csv.DictReader(csvfile)
         for row in reader:
             if fieldnames==[]:
                 fieldnames=list(row.keys())
             if row['Action'] == 'Add':
                 if row['crDOI'] == "":
                     print("Missing Identifier", row['Title'], row['Num'])
                 else:
                     catalysis_articles[int(row['Num'])]=row

    # print(len(catalysis_articles))
    # build new article and author tables
    # list of articles from crossref using DOIs
    cr_articles = {} # Num (from CHUK), DOI, type, and other fiedls from CR.
    article_columns=["NumUKCH"]
    # list of article authors from cross ref
    cr_authors = {} # AuthorNum, Firstname, Middle name, Last Name
    author_columns = ["AuthorNum", "Name", "LastName", "ORCID", 'affiliations','sequence']
    # list of article-author links
    cr_article_authour_link = {} # AuthorNum, DOI
    article_authour_columns = ["DOI","AuthorNum"]

    ## NumUKCH 	        : 1
    ## indexed 	        : [2019, 11, 11]
    ## reference-count 	: 52
    ## publisher 	        : Springer Science and Business Media LLC
    ## issue 	        : 10
    ## license 	        : http://www.springer.com/tdm
    ## funder 	        : None
    ## content-domain 	: None
    ## published-print 	: [2019, 10]
    ## DOI 	                : 10.1038/s41929-019-0334-3
    ## type 	        : article-journal
    ## created 	        : [2019, 9, 16]
    ## page 	        : 873-881
    ## update-policy 	: http://dx.doi.org/10.1007/springer_crossmark_policy
    ## source 	        : Crossref
    ## is-referenced-by-count : 0
    ## title 	        : Tuning of catalytic sites in Pt/TiO2 catalysts for the chemoselective hydrogenation of 3-nitrostyrene
    ## prefix 	        : 10.1038
    ## volume 	        : 2
    ## member 	        : 297
    ## published-online 	: [2019, 9, 16]
    ## reference 	        : None
    ## container-title 	: Nature Catalysis
    ## original-title 	: None
    ## language 	        : en
    ## link        	        : http://www.nature.com/articles/s41929-019-0334-3.pdf
    ## deposited 	        : [2019, 11, 11]
    ## score 	        : 1.0
    ## subtitle 	        : None
    ## short-title 	        : None
    ## issued        	: [2019, 9, 16]
    ## references-count 	: 52
    ## journal-issue 	: None
    ## alternative-id 	: None
    ## URL 	                : http://dx.doi.org/10.1038/s41929-019-0334-3
    ## relation 	        : None
    ## ISSN 	        : None
    ## container-title-short : Nat Catal
              
    for cat_art_num in catalysis_articles.keys():
        if catalysis_articles[cat_art_num]['crDOI'] != "":
            doi_text = catalysis_articles[cat_art_num]['crDOI']
            article_data = getCrossRefBibData(doi_text)
            data_keys = list(article_data.keys())
            for key in data_keys:
                if not (key in article_columns) and \
                   key not in ['author', 'assertion', 'indexed', 'funder',
                               'content-domain','created','update-policy', 'source',
                               'is-referenced-by-count','prefix','member',
                               'reference','original-title','language','deposited',
                               'score', 'subtitle', 'short-title', 'issued',
                               'alternative-id','relation','ISSN','container-title-short']:
                    article_columns.append(key)
            new_row = {}
            
            for key in article_columns:
                if key == 'NumUKCH':
                    new_row['NumUKCH'] = cat_art_num
                else:
                    if key in article_data.keys():
                        new_row[key] = jsonToPlainText(article_data[key])
            cr_articles[cat_art_num] = new_row
            for author in article_data['author']:
                new_author={}
                aut_num = len(cr_authors) + 1
                new_author["AuthorNum"] = aut_num
                new_author['LastName'] = author['family']
                if 'given' in author.keys():
                    new_author['Name'] = author['given']
                if 'given' in author.keys():
                    new_author['sequence'] = author['sequence']
                if 'ORCID' in author.keys():
                    new_author['ORCID'] = author['ORCID']
                else:
                    new_author['ORCID'] = "None"
                if 'affiliation'in author.keys():
                    affiliations=""
                    for affl in author['affiliation']:
                        affiliations += affl['name'] + "|"
                    new_author['affiliations'] = affiliations
                cr_authors[aut_num] = new_author
                art_auth_link = len(cr_article_authour_link)+1
                new_art_auth_link={}
                new_art_auth_link['DOI'] = doi_text
                new_art_auth_link['AuthorNum'] = aut_num
                cr_article_authour_link[art_auth_link] = new_art_auth_link
            #print(article_data['author'])
            
            
        
    # write back to a new csv file
    # create three files
    arts_file = input_file[:-4]+"Articles.csv"
    auts_file = input_file[:-4]+"Authors.csv"
    link_file = input_file[:-4]+"ArtAutLink.csv"
    with open(arts_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = article_columns)
        writer.writeheader()
        for cat_art_num in cr_articles.keys():
            writer.writerow(cr_articles[cat_art_num])

    with open(auts_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = author_columns)
        writer.writeheader()
        for aut_num in cr_authors.keys():
            writer.writerow(cr_authors[aut_num])


    with open(link_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = article_authour_columns)
        writer.writeheader()
        for link_num in cr_article_authour_link.keys():
            writer.writerow(cr_article_authour_link[link_num])

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

def remove_breaks(str_text):
    if "\n" in str_text:
        str_text = str_text.replace("\n", " ")
    return str_text

def remove_last_bar(str_text):
    return str_text[:-1]

def count_affiliations(str_text):
    return str_text.count("|") + 1

def get_affi_fields():
    affi_fields = { 'c':["Country", False], 'd':["Department", False],
                    'f':["Faculty", False], 'g':["Group", False],
                    'i':["Institution", False], 'u':["Unit", False]} 
    return affi_fields
    

def search_affi_institution(db_con, str_institution, new_affi):
    sql_query = "SELECT affiliations.id, affiliation_addresses.id, trim( affiliations.institution ||' '||" + \
                " affiliations.department ||' '|| affiliations.faculty ||' '||"+ \
                " affiliations.work_group) AS affi_str, trim(affiliation_addresses.add_01 ||' '||"+ \
                " affiliation_addresses.add_02  ||' '|| affiliation_addresses.add_03  ||' '||" + \
                " affiliation_addresses.add_04) ||' '|| affiliation_addresses.country AS add_str"+ \
                " FROM affiliations INNER JOIN affiliation_addresses "+ \
                " ON affiliations.id = affiliation_addresses.affiliation_id "+ \
                " WHERE affiliations.institution LIKE '%"+ str_institution+"%'"
    #print(sql_query)
    i_index = 0
    selected = 0
    selected_score = 0
    affiliations = db_con.execute(sql_query).fetchall()
    for affi in affiliations:
        #print(affi, new_affi)
        similarity = similar(new_affi.lower(), (affi[2]+" " +affi[3]).lower())
        if similarity > 0.8:
            if similarity > selected_score:
                selected = i_index
                selected_score = similarity
        i_index += 1
        
    if selected_score > 0:
        print("Found similar in DB")
        print(affiliations[selected][0], affiliations[selected][1], affiliations[selected][2]+" " +affiliations[selected][3], selected_score)
        user_opt = ""
        while True:
            print('Options:\n a) use\n b) skip\n selection:')
            user_opt = input()
            if user_opt in ['a', 'b']:
                break
        if user_opt == 'a':
            return int(affiliations[selected][0]), int(affiliations[selected][1])
    return 0, 0        
    
def get_value_list(db_con, table, field):
    results = db_con.execute("SELECT %s from %s GROUP BY %s" % (field, table, field) ).fetchall( )
    value_list = []
    for result in results:
        for item in result:
            value_list.append(item)
    if '' in value_list: value_list.remove('')
    return value_list

def get_affiliation(db_con, affi_id):
    db_affi = db_con.execute(
            "SELECT * FROM affiliations WHERE id = '%s'" % affi_id).fetchone( )
    return db_affi


def get_address(db_con, addr_id):
    db_addr = db_con.execute(
            "SELECT * FROM affiliation_addresses WHERE id = '%s'" % addr_id).fetchone( )
    return db_addr

def split_and_assign(input_text):
    ret_parsed = {}
    fields={'a':'ResearchGroup', 'b':'Department','c':'Faculty','d':'Institution',
            'e':'Address','f':'City','g':'Country','h':'Postcode'}
    if isinstance(input_text, str):
        user_opt = ""
        while True:
            print(input_text)
            print('Options:\n a) split\n b) assign\n selection:')
            user_opt = input()
            if user_opt in ['a', 'b']:
                break
        if user_opt == 'a':
            print("split separator (;,|):")
            separator = input()
            parts = input_text.split(separator)
            for part in parts:
                print("look up in db:",part)
                ass_affi, ass_add = search_affi_institution(db_con, part.strip(), input_text)
                print(ass_affi, ass_add)
                if ass_affi != 0:
                    print(get_affiliation(db_con, ass_affi))
                    print(get_address(db_con, ass_add))
                    ret_parsed={'affiliation_id':ass_affi, "address_id":ass_add}
                    return ret_parsed
                else:
                    ret_parsed.update(split_and_assign(part.strip()))
                
        elif user_opt == 'b':
            assgnr = ""
            strip_val = input_text.strip()
            search_affi_institution(db_con, strip_val, input_text)
            while True:
                if strip_val in institutions_list:
                    print('assing to:', "Institution")
                    ret_parsed["Institution"] = strip_val
                    break;
                elif strip_val in countries_list:
                    print('assing to:', "Country")
                    ret_parsed["Country"] = strip_val
                    break;
                elif input_text.strip() in countries_list:
                    print('assing to:', "Country")
                    ret_parsed["Country"] = input_text.strip()
                    break;
                
                print('Options:\n a) ResearchGroup\n b) Department\n c) Faculty\n d) Institution\n e) Address\n f) City\n g) Country\n h) Postcode')
                assgnr = input()
                print(assgnr)
                keys = list(fields.keys())
                print(keys)
                if assgnr in keys:
                    print('assing to:', assgnr, fields[assgnr])
                    ret_parsed[fields[assgnr]]=input_text.strip()
                    break;
    return ret_parsed

#split a single affiliation
def split_single_affiliation(affi_entry, assigned_list, entries_processed, affi_num, a_num):
    if affi_entry in  entries_processed.values():
        for entry in list(entries_processed):
            if entries_processed[entry] == affi_entry:
                assigned_list[affi_num] = assigned_list[entry].copy()
                assigned_list[affi_num]["AuthorNum"] = a_num
                entries_processed[affi_num] = affi_entry
                affi_num += 1
    else:
        print("split one affiliation")
        assigned = split_and_assign(affi_entry)
        assigned_list[affi_num]=assigned
        assigned_list[affi_num]["AuthorNum"] = a_num
        entries_processed[affi_num] = affi_entry
        affi_num += 1
    return affi_num, assigned_list, entries_processed

#split more than one affiliation
def split_mto_affiliation(affi_entries, assigned_list, entries_processed, affi_num, a_num):
    print("Split more than one affiliation from:", affi_entries)
    print("split separator (;,|):")
    separator = input()
    parts = affi_entries.split(separator)
    for part in parts:
        print("********************MULTIPLE**********************************")
        print(part.strip(), affi_num, a_num)
        affi_num, assigned_list, entries_processed = split_single_affiliation(part.strip(), assigned_list, entries_processed, affi_num, a_num)
        print(assigned_list)
        print(entries_processed)
    return affi_num, assigned_list, entries_processed

def split_affiliations(db_con, auth_file, link_file):
    
    affi_num = 1
    assigned_list = {}
    auth_records, auth_fields = get_data(auth_file, 'AuthorNum')
    link_records, likn_fields = get_data(link_file, 'AuthorNum')
    entries_processed = {}
    for a_num in auth_records:
        if auth_records[a_num]['affiliations'] != "":
            auth_records[a_num]['affiliations'] = remove_breaks(auth_records[a_num]['affiliations'])
            auth_records[a_num]['affiliations'] = remove_last_bar(auth_records[a_num]['affiliations'])
            affiliations = count_affiliations(auth_records[a_num]['affiliations'])
            print("***********************************************************")
            print("Affiliations", affiliations, auth_records[a_num]['affiliations'])
            #ask is single or multiple affiliations
            answer = sinlge = False
            if affiliations > 1:
                # ask if number of  affiliation is correct
                while answer == False:
                    print("a - single affiliation")
                    print("b - multiple affiliations")
                    print("Selection:")
                    usr_select = input()
                    if usr_select == 'a':
                        affi_entry = auth_records[a_num]['affiliations']
                        affi_numaffi_num, assigned_list, entries_processed = split_single_affiliation(affi_entry, assigned_list, entries_processed, affi_num, a_num)
                        print(assigned_list)
                        print(entries_processed)
                        answer = True
                    elif usr_select == 'b':
                        affi_entry = auth_records[a_num]['affiliations']
                        affi_numaffi_num, assigned_list, entries_processed = split_mto_affiliation(affi_entry, assigned_list, entries_processed, affi_num, a_num)
                        answer = True
            else:
                # split one affiliation
                affi_entry = auth_records[a_num]['affiliations']
                affi_num, assigned_list, entries_processed = split_single_affiliation(affi_entry, assigned_list, entries_processed, affi_num, a_num)                    
                print(assigned_list)
                print(entries_processed)
            if affi_num > 4:
                break
    return assigned_list
            #print(link_records[a_num])
    print('******************FINAL*******************************')
    print(assigned_list)
    print(entries_processed)

    #print("Countries:", countries_list,"\nInstitutions:", institutions_list,"\nDepartments:", department_list,"\nFaculties", faculty_list,"\nGroups:", group_list)        
    
dbname = 'ukch_articles.sqlite'
db_con = sqlite.connect(dbname)
art_doi = "10.1038/s41929-019-0334-3"
title = db_con.execute(
    "SELECT title from Articles where DOI='%s'" % art_doi).fetchone( )

# open update actions file
arts_file = 'UKCH202001b.csv'

input_file = "UKCH202001c.csv"
output_file = "UKCH202001d.csv"
# Check if article in DB
#check_articles_db(db_con, input_file, output_file)

# Get DOIS for articles not in DB
input_file = "UKCH202001d.csv"
output_file = "UKCH202001e.csv"
#get_articles_doi(input_file, output_file)

# Verify DOIS for articles not in DB
input_file = "UKCH202001e.csv"
output_file = "UKCH202001f.csv"
#verify_articles_doi(input_file, output_file)

input_file = "UKCH202001f.csv"
# build the records ready to load into DB
#buildDBfromJSON(input_file)

arts_file = input_file[:-4]+"Articles.csv"
auts_file = input_file[:-4]+"Authors.csv"
link_file = input_file[:-4]+"ArtAutLink.csv"
afi_file = "affiliations201912.csv"
addr_file = "affiliations201912.csv"

# get institutions list from affiliations table
institutions_list = get_value_list(db_con, "Affiliations", "institution")
# get coutries from affiliations table
countries_list = get_value_list(db_con, "Affiliations","country")
# get department list from affiliations table
department_list = get_value_list(db_con, "Affiliations","department")
# get faculty list from affiliations table
faculty_list = get_value_list(db_con, "Affiliations","faculty")
# get research group list from affiliations table
group_list = get_value_list(db_con, "Affiliations", "work_group")

affiliations = split_affiliations(db_con, auts_file, link_file)

#add_new_articles(db_con, arts_file)
#add_new_authors()
#add_affiliation_author_link(db_con)
#verify_addresses(db_con)
#verify_themes(db_con)


