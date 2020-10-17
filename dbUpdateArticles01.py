# code duplication, need to streamline/refactor
# separate into classes
# create methods and properties

import csv
import string
from sqlite3 import dbapi2 as sqlite
from difflib import SequenceMatcher
import requests
from bs4 import BeautifulSoup

from habanero import Crossref
from habanero import cn
import json

import datetime

cr = Crossref()

def similar(a, b):
    print("&&&Similarity:", a,b)
    return SequenceMatcher(None, a,b).ratio()


def getHTMLPage(url):
    soup = None
    try:
        req_head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        response = requests.get(url, headers = req_head)
        soup = BeautifulSoup(response.text,'html.parser')
    except Exception as e:
        print(e)
    return soup

def getParagraphs(soup):
    result = []
    try:
        for para in soup.find_all('p'):
            result.append(para)
    except Exception as e:
        print(e)
    return result


def add_articles(con, input_file):
    catalysis_articles = {}
    fieldnames=[]
    date_stamp = datetime.datetime.now().date().strftime('%Y%m%d')
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if fieldnames==[]:
                fieldnames=list(row.keys())
            catalysis_articles[int(row['id'])]=row
    for new_art_id in catalysis_articles.keys():
        art_doi = catalysis_articles[new_art_id]['doi']
        title = con.execute(
             "SELECT title from Articles where DOI='%s'" % art_doi).fetchone( )
        top_id = con.execute(
             "SELECT MAX(id) from Articles").fetchone( )[0]
        if str(type(title)) != "<class 'NoneType'>" and len(title) > 0:
             print("Found:", title[0])
        else:
            print("Not Found:", art_doi)
            print("inserting")
            # build column list
            csv_id = catalysis_articles[new_art_id]['id']
            catalysis_articles[new_art_id]['id'] = int(top_id) + 1
            catalysis_articles[new_art_id]['status'] = "added " + date_stamp 
            columns = str(tuple(catalysis_articles[new_art_id].keys())).replace("'", "")
            values = str(tuple(catalysis_articles[new_art_id].values()))
            print("INSERT INTO Articles %s VALUES  %s " % (columns, values))
            ins = con.execute(
             "INSERT INTO Articles %s VALUES  %s " % (columns, values)).fetchone( )
            catalysis_articles[new_art_id]['csv_id'] = csv_id
        con.commit()
    write_csv(catalysis_articles, input_file)


def add_csv_authors(con, author_file, link_file, affi_link_file = "", affis_file = ""):
    # Select all authors from author update,
    # look up in article link
    # if article added then
    #    look up in authors,
    #    if found then get ID for creating Author-Article Link
    #    if not found then add author and create Author-Article Link
    new_authors, author_fields = get_data(author_file, "id")
    new_links, link_fields = get_data(link_file, "author_id")
    if affi_link_file != "":
        new_affi_links, affi_link_fields = get_data(affi_link_file, "id")
    else:
        new_affi_links = affi_link_fields = None
    if affis_file != "":
        new_affis, affi_fields = get_data(affis_file, "id")
        add_csv_affiliations(con, affis_file)
        new_affis, affi_fields = get_data(affis_file[:-4]+"1.csv", "id")
    else:
        new_affis = affi_fields = None
    i_found = 0
    i_not_found = 0
    date_stamp = datetime.datetime.now().date().strftime('%Y%m%d')
    for na_index in new_authors:
        new_author = new_authors[na_index]
        # LookUp by ORCID
        author_ID = 0
        na_ORCID = new_author["orcid"]
        na_fullname = new_author['last_name'] + ", " + new_author['given_name']
        na_name = new_author['given_name']
        na_lastname = new_author['last_name']
        na_num = new_author['id']
        na_sequence = new_author['sequence']
        # Lookup Authors and if needed add
        author_ID = get_author_id(con, na_fullname,na_name,na_lastname,na_ORCID)
        top_id = get_max_id(con,"authors")
        print("Author DB ID:", author_ID)
        if author_ID == None or author_ID == -1:
            i_not_found += 1
            print("&&&Not Found", i_not_found, new_author)
            top_id += 1
            author_ID = top_id
            # Need to add to the DB, before creating article-author-link
            new_author = {'full_name':na_fullname, "last_name":na_lastname, "given_name":na_name, "orcid":na_ORCID, "articles":0, 'id':author_ID}
            author_fields = ['full_name', "last_name", "given_name", "orcid", "articles","id"]
            add_authors(con, new_author, author_fields)
            print('ADDED AUTHOR:', author_ID)
        else:
            i_found += 1
            print("Found", i_found, new_author)
            # no need to add, just create article-author-link
        # create author link
        new_author['db_id']=author_ID
        max_id = get_max_id(con, "article_author_links")
        link_doi = ""
        for link in new_links:
            if new_links[link]["author_id"] == na_num:
                link_doi = new_links[link]["doi"]
                new_link = {'doi':new_links[link]["doi"], "author_id":author_ID,
                            "author_count":new_links[link]["count"],
                            "author_order":new_links[link]["order"],
                            "status":"Added"+date_stamp,
                            "sequence":na_sequence, "id":str(max_id + 1)}
                add_links(con, new_link)
        if new_affi_links != None:
            print("Adding Affiliations")
            for affi_link_id in new_affi_links:
                new_affi_link =  new_affi_links[affi_link_id]
                #print(new_affi_link)
                if new_affi_link['AuthorNum'] == na_num:
                    new_affi_link_id = get_max_id(con, "affiliation_links")+1
                    na_link ={'id':new_affi_link_id, 'doi':link_doi,
                                        "author_id":author_ID,"sequence":na_sequence}
                    if new_affi_link['affiliation_id']!='0':
                        na_link["affiliation_id"] = new_affi_link['affiliation_id']
                        na_link["address_id"] = new_affi_link['address_id']
                    else:
                        #need to lookup ids assigned to new affiliaition
                        for na_id in new_affis:
                            if new_affis[na_id]['id'] == new_affi_link['new_afi_id']:
                                na_link["affiliation_id"] = new_affis[na_id]['db_id']
                                na_link["address_id"] = new_affis[na_id]['address_id']
                    add_affi_links(con, na_link)        
                        
        
    write_csv(new_authors, author_file[:-4]+"1.csv")
    write_csv(new_links, link_file[:-4]+"1.csv")


def add_authors(con, author, fieldnames):
        aut_id = author['id']
        print("adding:", aut_id)
        # build column list
        columns = str(tuple(author.keys())).replace("'", "")
        values = str(tuple(author.values()))
        ins = con.execute(
            "INSERT INTO Authors %s VALUES  %s " % (columns, values)).fetchone( )
        con.commit()
        print("Author Added", ins)

def add_links(con, art_aut_link):
    art_doi = art_aut_link['doi']
    aut_id = art_aut_link['author_id']
    #affi_id = art_aut_link['affiliation_id']
    link_doi = con.execute(
         "SELECT DOI from Article_author_Links where doi='%s' and author_id = '%s'" % (art_doi, aut_id)).fetchone( )
    if str(type(link_doi)) != "<class 'NoneType'>" and len(link_doi) > 0:
         print("Found:", link_doi[0])
    else:
        print("&&&Not Found:", art_doi, "inserting", art_aut_link)
        # build column list
        columns = str(tuple(art_aut_link.keys())).replace("'", "")
        values = str(tuple(art_aut_link.values()))
        ins = con.execute(
            "INSERT INTO Article_Author_Links %s VALUES  %s " % (columns, values)).fetchone( )
        con.commit()

def add_affi_links(con, affi_link):
    art_doi = affi_link['doi']
    aut_id = affi_link['author_id']
    link_doi = con.execute(
         "SELECT DOI from affiliation_Links where doi='%s' and author_id = '%s' and affiliation_id = '%s'" % (art_doi, aut_id, affi_id)).fetchone( )
    if str(type(link_doi)) != "<class 'NoneType'>" and len(link_doi) > 0:
         print("Found:", link_doi[0])
    else:
        print("===Not Found:", art_doi, "inserting", affi_link)
        # build column list
        columns = str(tuple(affi_link.keys())).replace("'", "")
        values = str(tuple(affi_link.values()))
        ins = con.execute(
            "INSERT INTO affiliation_links %s VALUES  %s " % (columns, values)).fetchone( )
        con.commit()

def add_affiliation(con, affiliation):
        print("adding:", affiliation)
        # build column list
        columns = str(tuple(affiliation.keys())).replace("'", "")
        values = str(tuple(affiliation.values()))
        con.execute(
            "INSERT INTO affiliations %s VALUES  %s " % (columns, values)).fetchone( )
        con.commit()
        
def add_address(con, address):
        print("adding:", address)
        # build column list
        columns = str(tuple(address.keys())).replace("'", "")
        values = str(tuple(address.values()))
        con.execute(
            "INSERT INTO affiliation_addresses %s VALUES  %s " % (columns, values)).fetchone( )
        con.commit()
        
def add_csv_affiliations(con, affis_file):
    # Need to add affiliation before authors
    # becuase need the DB affiliation ids
    # for the links to authors and publications
    
    # look up in article link
    # if article added then
    #    look up in authors,
    #    if found then get ID for creating Author-Article Link
    #    if not found then add author and create Author-Article Link

    # open the affiliation file
    if affis_file != "":
        new_affis, affi_fields = get_data(affis_file, "id")
    else:
        new_affis = affi_fields = None
    i_found = 0
    i_not_found = 0
    date_stamp = datetime.datetime.now().date().strftime('%Y%m%d')
    processed = {}
    counter = 1
    keys = {}
    for afi_index in new_affis:
        new_affi = new_affis[afi_index]
        str_affi = ",".join(list(new_affi.values())[2:])
        #print(str_affi)
        if not str_affi in processed.values():
            affi_id = get_max_id(con, 'affiliations') + 1
            add_id = get_max_id(con, 'affiliation_addresses') + 1
            processed[counter] = str_affi
            counter +=1
            affiliation = {'id':affi_id, 'institution':new_affi['Institution'], 'department':new_affi['Department'],
                           'faculty':new_affi['Faculty'],
                           'work_group':new_affi['ResearchGroup'],
                           'country':new_affi['Country']}
            address = {'id':add_id,'country':new_affi['Country'],'affiliation_id':affi_id}
            if new_affi['Address'] != '':
                address['add_01'] = new_affi['Address']
            elif new_affi['City'] != '':
                address['add_01'] = new_affi['City']
            else:
                address['add_01'] = new_affi['Address']
                address['add_02'] = new_affi['City']
                
            print('New Affiliation:', affiliation)
            #add affiliation to db
            add_affiliation(con, affiliation)
            print('New Address:', address)
            # add address to db
            add_address(con, address)
            new_affi['db_id'] = affi_id
            new_affi['address_id'] = add_id
            keys[str_affi] = [affi_id, add_id]

        else:
            new_affi['db_id'] = keys[str_affi][0]
            new_affi['address_id'] = keys[str_affi][1]
            
    # write back to csv with new keys
    for afi_index in new_affis:
        print(new_affis[afi_index])
    write_csv(new_affis, affis_file[:-4]+"1.csv")    


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

def get_max_id(con, table_name):
    max_id = con.execute("SELECT MAX(id) FROM "+ table_name).fetchone( )
    return max_id[0]

def get_max_aut_id(con):
    db_author = con.execute("SELECT MAX(id) FROM Authors").fetchone( )
    return db_author[0]

def get_author_id(con, fullname, givenname, lastname, ORCID = ""):
    id = -1
    db_author = con.execute(
        "SELECT * FROM Authors WHERE full_name='%s'" % fullname.replace("'","''")).fetchone( )
    #print("FULL MATCH",a_full, a_id, db_author)
    if not db_author is None:
        id = db_author[5]
    elif db_author is None and ORCID != '':
        db_author = con.execute(
            "SELECT * FROM Authors WHERE orcid = '%s'" % ORCID).fetchone( )
        if not db_author is None:
            print("ORCID MATCH:", db_author, fullname, ORCID, db_author[3])
            id = db_author[5]  
    else:
    # try to match by last name using similarity
        db_authors = con.execute(
            "SELECT * FROM Authors WHERE last_name LIKE '"+"%"+ lastname.replace("'","''")+"%"+"'").fetchall( )
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
            "SELECT * FROM Authors WHERE given_name LIKE '"+"%"+ givenname.replace("'","''")+"%"+"'").fetchall( )
        if not db_authors is None:
            for db_author in db_authors:
                print ("&&&DB Author", db_author)
                similarity = similar(fullname, db_author[1]) # index of full name changed
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
            print("** Not Found", i_not_found, new_author)
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


def add_address_id_to_affi_link(db_con):
    # Lookup Affiliation link in affiliations and add affiliation address ids
    # 
    # records from affiliation links whith no address_id
    affi_links = \
                    db_con.execute(
                        "SELECT id, affiliation_id FROM affiliation_links WHERE address_id is null ").fetchall( )
    # records from address linked to only one affilition
    one_add_affis = \
                    db_con.execute(
                        "SELECT affiliation_addresses.id, affiliation_addresses.affiliation_id FROM affiliation_addresses group by affiliation_addresses.affiliation_id HAVING count() = 1").fetchall( )
    temp = {}
    for affi_id in one_add_affis:
        temp[affi_id[1]] = affi_id[0]
    one_add_affis = temp
    # records from address linked to only one affilition
    many_add_affis = db_con.execute(
                        "SELECT affiliation_addresses.id, affiliation_addresses.affiliation_id FROM affiliation_addresses group by affiliation_addresses.affiliation_id HAVING count() > 1").fetchall( )
    temp = {}
    for affi_id in many_add_affis:
        temp[affi_id[1]] = affi_id[0]
    many_add_affis = temp
    # records  from temp affilitions table with original affiliation string
    affi_strings = ""#hack # db_con.execute(
                     #   "SELECT AffiLinkID, UniqueID, affiliations FROM Affiliation_Links20191218").fetchall( )
    
    i_found = 0
    i_not_found = 0
    for link_id_affi in affi_links:
        link_id = link_id_affi[0]
        affi_id = link_id_affi[1]
        #verify if affiliation has unique address registered
        if affi_id in one_add_affis.keys():
            # set the address to the unique address in DB
            add_id = one_add_affis[affi_id]
            db_con.execute("UPDATE affiliation_links SET address_id = '%s' WHERE id = '%s'" %(add_id, link_id)).fetchone( )
            db_con.commit()
        else:
            #get all addresses for affi
            address_for_affi = db_con.execute(
                        "SELECT id, add_01, add_02, add_03, add_04, affiliation_id FROM affiliation_addresses WHERE affiliation_id = '%s'"% affi_id).fetchall( )
            #get the original string for affi
            affi_string = db_con.execute(
                        "SELECT affiliations FROM Affiliation_Links20191218 WHERE AffiLinkID = '%s'" % link_id).fetchone( )[0]
            #print("AFFILIATION:", affi_string)
            likely = 0
            likely_count = 0
            max_likely = 0
            for address in address_for_affi:
                add_id = address[0]
                add_01 = address[1]
                add_02 = address[2]
                add_03 = address[3]
                add_04 = address[4]
                #print (address)
                if add_01 != "" and add_01 in affi_string:
                    likely_count +=1
                if add_02 != "" and add_02 in affi_string:
                    likely_count +=1
                if add_03 != "" and add_03 in affi_string:
                    likely_count +=1
                if add_04 != "" and add_04 in affi_string:
                    likely_count +=1
                if likely_count > max_likely:
                    max_likely = likely_count
                    likely = add_id
                likely_count = 0      
            if likely != 0:
                #print (likely)
                db_con.execute("UPDATE affiliation_links SET address_id = '%s' WHERE id = '%s'" %(likely, link_id)).fetchone( )
                db_con.commit()
            
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
pub_urls = ['https://ukcatalysishub.co.uk/publications', 'https://ukcatalysishub.co.uk/biocatalysis-publications-2018/',
            'https://ukcatalysishub.co.uk/design-publications-2018/','https://ukcatalysishub.co.uk/energy-publications-2018/',
            'https://ukcatalysishub.co.uk/transformations-publications-2018/','https://ukcatalysishub.co.uk/environment-publications-2018/'
            'https://ukcatalysishub.co.uk/biocatalysis-publications-2017/',
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
        

def map_themes(db_con, input_file, output_file):
    site_articles, article_fileds = get_data(input_file, "Num")
    i_counter = 0
    for pub_url in pub_urls:
        print(pub_url, pub_urls.index(pub_url))
        group_index = pub_urls.index(pub_url)
        parsed_page = getHTMLPage(pub_url)
        list_of_paragraphs = getParagraphs(parsed_page)
        for num in site_articles:
            if not 'Themes' in site_articles[num].keys():
                site_articles[num]['Themes']=""
            #print(site_articles[num]['Title'])
            str_title = site_articles[num]['Title']
            for x in list_of_paragraphs:
                #print(x)
                if str_title in str(x):
                    if site_articles[num]['Themes'] == "":
                        site_articles[num]['Themes'] =  str(group_index)
                    else: 
                        site_articles[num]['Themes'] +=  "," +str(group_index)
    write_csv(site_articles, output_file)
    
    

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
            print(row.keys())
            catalysis_articles[int(row['NumUKCH'])]=row
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
    

def write_csv(values, filename):
    fieldnames = []
    for item in values.keys():
        for key in values[item].keys():
            if not key in fieldnames:
                fieldnames.append(key)
    #write back to a new csv file
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key in values.keys():
            writer.writerow(values[key])


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
    input_text = input_text.strip()
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
                ret_parsed.update(split_and_assign(part.strip()))
        elif user_opt == 'b':
            assgnr = ""
            while True:
                if input_text in institutions_list:
                    print('assing to:', "Institution")
                    ret_parsed["Institution"] = input_text
                    break;
                elif input_text in countries_list:
                    print('assing to:', "Country")
                    ret_parsed["Country"] = input_text
                    break;
                elif input_text in department_list:
                    print('assing to:', "Department")
                    ret_parsed["Department"] = input_text
                    break;
                print('Options:\n a) ResearchGroup\n b) Department\n c) Faculty\n d) Institution\n e) Address\n f) City\n g) Country\n h) Postcode')
                assgnr = input()
                #print(assgnr)
                keys = list(fields.keys())
                #print(keys)
                if assgnr in keys:
                    print('assing to:', assgnr, fields[assgnr])
                    ret_parsed[fields[assgnr]]=input_text
                    if assgnr == 'd' and not input_text in institutions_list:
                        #institution
                        institutions_list.append(input_text)
                    elif assgnr == 'b' and not input_text in department_list:
                        #department
                        department_list.append(input_text)
                    elif assgnr == 'e' and not input_text in address_list:
                        address_list.append(input_text)
                    break;
    return ret_parsed

#split a single affiliation
def split_single_affiliation(affi_entry, assigned_list, entries_processed, affi_num, a_num):
    if affi_entry in  entries_processed.values():
        for entry in list(entries_processed):
            if entries_processed[entry] == affi_entry:
                assigned_list[affi_num] = assigned_list[entry].copy()
                assigned_list[affi_num]["AuthorNum"] = a_num
                assigned_list[affi_num]["id"] = affi_num
                entries_processed[affi_num] = affi_entry
    else:
        print("split one affiliation")
        assigned = split_and_assign(affi_entry)
        assigned_list[affi_num]=assigned
        assigned_list[affi_num]["AuthorNum"] = a_num
        assigned_list[affi_num]["id"] = affi_num
        entries_processed[affi_num] = affi_entry
    return affi_num, assigned_list, entries_processed

#split more than one affiliation
def split_mto_affiliation(affi_entries, assigned_list, entries_processed, affi_num, a_num):
    print("Split more than one affiliation from:", affi_entries)
    #print("split separator (;,|):")
    #separator = input()
    separator = "|"
    affi_entries.split(separator)
    return affi_entries.split(separator)


def split_affiliations(db_con, auth_file, link_file):
    
    affi_num = 1
    assigned_list = {}
    auth_records, auth_fields = get_data(auth_file, 'AuthorNum')
    link_records, likn_fields = get_data(link_file, 'AuthorNum')
    entries_processed = {}
    # first pass split multiple affiliations
    # go trough all authors, and if multiple split, replace record with new affiliation and add a new affiliation for author
    additional_aut_records = {}
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
                    print("a - multiple affiliations")
                    print("b - single affiliation")
                    print("Selection:")
                    usr_select = input()
                    affi_entry = auth_records[a_num]['affiliations']
                    if usr_select == 'a':
                        affiliations = split_mto_affiliation(affi_entry, assigned_list, entries_processed, affi_num, a_num)
                        print(affiliations)
                        index_affis = 0
                        for index_affis in range(0, len(affiliations)):
                            if index_affis == 0:
                                auth_records[a_num]['affiliations'] = affiliations[index_affis]
                            else:
                                new_id = len(additional_aut_records) + len(auth_records)+1
                                additional_aut_records[new_id] = auth_records[a_num].copy()
                                additional_aut_records[new_id]['affiliations'] = affiliations[index_affis]
                        answer = True
                    if usr_select == 'b':
                        # convert to single by replacing separtor for ;
                        auth_records[a_num]['affiliations'] = affi_entry.replace("|", ";")
                        print(auth_records[a_num]['affiliations'])
                        answer = True
    
    
    print(additional_aut_records)
    auth_records.update(additional_aut_records)
    write_csv(auth_records, "test01.csv")
    auth_records, auth_fields = get_data("test01.csv","id")
    
    print(len(auth_records),auth_records[len(auth_records)])
    # second pass look up in DB for similars use full text
    sql_query = "SELECT affiliations.id, affiliation_addresses.id, trim( affiliations.department ||' '||" + \
                " affiliations.institution ||' '|| affiliations.faculty ||' '||"+ \
                " affiliations.work_group) AS affi_str, trim(affiliation_addresses.add_01 ||' '||"+ \
                " affiliation_addresses.add_02  ||' '|| affiliation_addresses.add_03  ||' '||" + \
                " affiliation_addresses.add_04) ||' '|| affiliation_addresses.country AS add_str"+ \
                " FROM affiliations INNER JOIN affiliation_addresses "+ \
                " ON affiliations.id = affiliation_addresses.affiliation_id "
    
    
    db_affis = db_con.execute(sql_query).fetchall()
    for a_num in auth_records:
        auth_records[a_num]['affiliation_id'] =  0
        auth_records[a_num]['address_id'] = 0
        if auth_records[a_num]['affiliations'] != "":
            i_index = 0
            selected = 0
            selected_score = 0
            print(auth_records[a_num])
            affi_entry = auth_records[a_num]['affiliations']
            for affi in db_affis:
                #print(affi, new_affi)
                similarity = similar(affi_entry.lower(), (affi[2]+" " +affi[3]).lower())
                if similarity > 0.0:
                    if similarity > selected_score:
                        selected = i_index
                        selected_score = similarity
                i_index += 1
            if selected_score > 0:
                print("Found similar in DB")
                print(db_affis[selected], selected_score)
                print(db_affis[selected][0], db_affis[selected][1], db_affis[selected][2]+" " +db_affis[selected][3], selected_score)
                user_opt = ""
                while True:
                    print('Options:\n a) use\n b) skip\n selection:')
                    user_opt = input()
                    if user_opt in ['a', 'b']:
                        break
                if user_opt == 'a':
                    auth_records[a_num]['affiliation_id'] = db_affis[selected][0]
                    auth_records[a_num]['address_id'] = db_affis[selected][1]
                    #print(db_affis[selected][0]), int(db_affis[selected][1])
            affi_num = a_num
    write_csv(auth_records, "test02.csv")

    auth_records, auth_fields = get_data("test02.csv","id")
    for indexer in range(1, affi_num):
        print(auth_records[indexer])
    # third pass split affiliations
    for a_num in auth_records:
        print(auth_records[a_num])
        if auth_records[a_num]['affiliations'] != "" and auth_records[a_num]['affiliation_id'] == '0':
            affi_entry = auth_records[a_num]['affiliations']
            affi_num, assigned_list, entries_processed = split_single_affiliation(affi_entry, assigned_list, entries_processed, affi_num, a_num)
            auth_records[a_num]['new_afi_id'] = affi_num
            affi_num = a_num
    print('******************FINAL*******************************')
    print(assigned_list)
    print(entries_processed)
    write_csv(assigned_list, "new_affiliations.csv")
    write_csv(auth_records, "test03.csv")
    
dbname = 'ukch_articles.sqlite'
db_con = sqlite.connect(dbname)
art_doi = "10.1038/s41929-019-0334-3"
title = db_con.execute(
    "SELECT title from Articles where DOI='%s'" % art_doi).fetchone( )

### open update actions file
##arts_file = 'processed_csv/AddNewArticles202002.csv' #'UKCH202001b.csv'

#the name of the root file from wich Arts, auts and links were generated
## 20200624 input_file = 'processed_csv/AddNewArticles202002.csv' #UKCH202001Missing.csv
input_file = 'processed_csv/AddNewArticles202006UKCHPubs.csv' #UKCH202001Missing.csv

##output_file = input_file[:-4]+"A.csv"
### Check if article in DB
### check_articles_db(db_con, input_file, output_file)
##
### Get DOIS for articles not in DB
##input_file = "UKCH202001d.csv"
##output_file = "UKCH202001e.csv"
###get_articles_doi(input_file, output_file)
##
### Verify DOIS for articles not in DB
##input_file = "UKCH202001e.csv"
##output_file = "UKCH202001f.csv"
###verify_articles_doi(input_file, output_file)
##
##input_file = "UKCH202001f.csv"
### build the records ready to load into DB
###buildDBfromJSON(input_file)

arts_file = input_file[:-4]+"Articles.csv"
auts_file = input_file[:-4]+"Authors.csv"
link_file = input_file[:-4]+"ArtAutLink.csv"
afi_file = "processed_csv/affiliations201912.csv"
addr_file = "processed_csv/affiliations201912.csv"

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
address_list = []
#affiliations = split_affiliations(db_con, auts_file, link_file)

#add articles, authors article-author links and affiliations to the DB
add_articles(db_con, arts_file)
add_csv_authors(db_con, auts_file, link_file)#,"test03.csv","new_affiliations.csv")
add_address_id_to_affi_link(db_con)
##
### Map DOIS to themes and mark articles not in website
##input_file = "UKCH202001f.csv"
##output_file = "UKCH202001g.csv"
##map_themes(db_con, input_file, output_file)




#add_new_articles(db_con, arts_file)
#add_new_authors()
#add_affiliation_author_link(db_con)
#verify_addresses(db_con)
#verify_themes(db_con)

