# Libraries
# library containign functions that read and write to csv files
import lib.handle_csv as csvh
# library for connecting to the db
import lib.handle_db as dbh
# library for getting data from crossref
import lib.crossref_api as cr_api
# library for handling url searchs
import lib.handle_urls as urlh
# managing files and file paths
from pathlib import Path
#library for handling json files
import json
# library for using regular expressions
import re
# library for handling http requests
import requests

# manage configuration files (*.ini)
import configparser

# Read key value from a configuration file
def read_keys():
    ini_file = Path().absolute() /  "config/config.ini"
    api_keys ={}
    if ini_file.exists():
        seg_config = configparser.ConfigParser()
        seg_config.read(ini_file)
        api_keys['elsevier'] = seg_config['ApiKeys']["ElsevierMining"]
        api_keys['wiley'] = seg_config['ApiKeys']["WileyMining"]
    return api_keys

# Custom Functions
# ** will migrate to lib if needed for more than one notebook

# get the crossreference json page from doi
def get_cr_json_object(cr_doi):
  crjd = None
  doi_file = 'json_files/' + cr_doi.replace('/','_').lower() + '.json'
  if not Path(doi_file).is_file():
    crjd = cr_api.getBibData(cr_doi)
    with open(doi_file, 'w', encoding='utf-8-sig', errors='ignore') as f:
                json.dump(crjd, f, ensure_ascii=False, indent=4)
  else:
    with open(doi_file, 'r', encoding='utf-8-sig') as jf:
        crjd = json.load(jf)
  # return the content and the file name 
  return crjd, doi_file

# get the landing page for the publication from uri
def get_pub_html_doi(cr_doi):
    html_file = 'html_files/' + cr_doi.replace('/','_').lower() + '.html'
    if not Path(html_file).is_file():
        page_content = urlh.getPageFromDOI(doi_text)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_content.decode("utf-8") )
    else:
        f = open(html_file, "r")
        page_content = f.read()
    return page_content, html_file

# get a list of titles from the previous searches database
def get_titles(str_pub_title, db_name = "prev_search.sqlite3"):
    print(db_name)
    db_conn = dbh.DataBaseAdapter(db_name)
    search_in = 'prev_pop_searches'
    fields_required = "Num, Title"
    filter_str = "Title like '"+str_pub_title[0]+"%';"

    db_titles = db_conn.get_values(search_in, fields_required, filter_str)
    db_conn.close()
    return db_titles

# get a list of ids, titles, and dois from the app database
def get_titles_and_dois(str_pub_title, db_name = "app_db.sqlite3"):
    print(db_name)
    db_conn = dbh.DataBaseAdapter(db_name)
    search_in = 'articles'
    fields_required = "id, title, doi"
    filter_str = "Title like '"+str_pub_title[0]+"%';"
    db_titles = db_conn.get_values(search_in, fields_required, filter_str)
    db_conn.close()
    return db_titles

# get a list of ids, titles, dois, links, and pdf_file 
# names from the data database
def get_pub_data(db_name = "app_db.sqlite3"):
    db_conn = dbh.DataBaseAdapter(db_name)
    search_in = 'articles'
    fields_required = "id, title, doi, link, pdf_file"
    filter_str = "status = 'Added'"
    db_titles = db_conn.get_values(search_in, fields_required, filter_str)
    db_conn.close()
    return db_titles

# get a list of ids, titles, dois, and links
# for pubs with no data from the app database
def get_pub_app_data(db_name = "app_db.sqlite3"):
    db_conn = dbh.DataBaseAdapter(db_name)
    search_in = 'articles'
    fields_required = "id, title, doi, link"
    filter_str = "status = 'Added'"
    db_titles = db_conn.get_values(search_in, fields_required, filter_str)
    db_conn.close()
    return db_titles


def get_pub_app_no_data(db_name = "app_db.sqlite3"):
    db_conn = dbh.DataBaseAdapter(db_name)
    search_in = 'articles'
    fields_required = "id, title, doi, link"
    filter_str = "status = 'Added'"
    db_pubs = db_conn.get_values(search_in, fields_required, filter_str)
    db_data_ids = db_conn.get_values("article_datasets", "article_id", "id > 0")
    db_data_ids = set(list(sum(db_data_ids,()))) # flatten list of tuples into set
    no_data_titles = []
    for a_pub in db_pubs:    
        if not a_pub[0] in db_data_ids:
            no_data_titles.append(a_pub)
    db_conn.close()
    return no_data_titles

def get_dataset_data(db_name = "app_db.sqlite3"):
    db_conn = dbh.DataBaseAdapter(db_name)
    search_in = 'datasets'
    fields_required = "id, dataset_doi, dataset_location, dataset_name"
    filter_str = "id > 0 "
    db_datasets = db_conn.get_values(search_in, fields_required, filter_str)
    return db_datasets

def get_pub_datasets(db_name = "app_db.sqlite3", db_id = 1):
    db_conn = dbh.DataBaseAdapter(db_name)
    search_in = 'article_datasets'
    fields_required = "dataset_id"
    filter_str = "article_id = '"+ str(db_id) +"'"
    db_data_ids = db_conn.get_values(search_in, fields_required, filter_str)
    db_data_ids = set(list(sum(db_data_ids,()))) # flatten list of tuples into set
    db_datasets = []
    if len(db_data_ids) > 0:
        search_in = "datasets"
        fields_required = "id, dataset_doi, dataset_location, dataset_name"
        filter_str = "id in "+ str(db_data_ids).replace('{','(').replace('}',')')
        db_datasets = db_conn.get_values(search_in, fields_required, filter_str)
    db_conn.close()
    return db_datasets

# get the current csv working file
def get_working_file(nr_wf):
    working_file = wf_fields = None
    current_pass = 0
    if Path(nr_wf).is_file():
        working_file, wf_fields = csvh.get_csv_data(nr_wf,'Num')
        for art_num in working_file:
            if 'ignore' in working_file[art_num].keys():
                if current_pass < int(working_file[art_num]['ignore']):
                    current_pass = int(working_file[art_num]['ignore'])
            else:
                break
    print("Current pass:", current_pass)
    return working_file, wf_fields, current_pass

# get an html file saved locally in the html_file folder 
def get_pub_html_url(text_url, entry_id):
    html_file = 'html_files/' +  entry_id + '.html'
    if not Path(html_file).is_file():
        print("")
        page_content = urlh.getPageFromURL(text_url)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_content)
    else:
        f = open(html_file, "r")
        page_content = f.read()
    return page_content, html_file

# use regular expression to check if a given string
# is a valid DOI, using pattern from CR
def valid_doi(cr_doi):
    # CR DOIS: https://www.crossref.org/blog/dois-and-matching-regular-expressions/
    # CR DOIs re1
    # /^10.\d{4,9}/[-._;()/:A-Z0-9]+$/i
    if cr_doi == None:
        return False
    cr_re_01 = '^10.\d{4,9}/[-._;()/:A-Z0-9]+'
    compare = re.match(cr_re_01, cr_doi, re.IGNORECASE)
    if compare != None and cr_doi == compare.group():
        return True
    else:
        return False
    
# get a semicolon separated list of authors from CR json data
def get_cr_author_list(article_data):
    authors = []
    if 'author' in article_data.keys():
        for author in article_data['author']:
            new_author=""
            new_author = author['family']
            if 'given' in author.keys():
                new_author += ", " + author['given']
            authors.append(new_author)
    return ("; ").join(authors)

# get the publication year from CR json data
def get_cr_year_published(article_data):
    year_print = 0
    if 'published-print' in article_data.keys() \
        and article_data['published-print'] != None \
        and article_data['published-print']['date-parts'][0] != None:
        year_print = int(article_data['published-print']['date-parts'][0][0])    
    elif 'journal-issue' in article_data.keys() \
        and article_data['journal-issue'] != None \
        and 'published-print' in article_data['journal-issue'].keys() \
        and article_data['journal-issue']['published-print'] != None \
        and article_data['journal-issue']['published-print']['date-parts'][0] != None:
        year_print = int(article_data['journal-issue']['published-print']['date-parts'][0][0])
    year_online = 0
    if 'published-online' in article_data.keys() \
        and article_data['published-online'] != None \
        and article_data['published-online']['date-parts'][0] != None:
        year_online = int(article_data['published-online']['date-parts'][0][0])    
    elif 'journal-issue' in article_data.keys() \
        and article_data['journal-issue'] != None \
        and 'published-online' in article_data['journal-issue'].keys() \
        and article_data['journal-issue']['published-online'] != None \
        and article_data['journal-issue']['published-online']['date-parts'][0] != None:
        year_print = int(article_data['journal-issue']['published-online']['date-parts'][0][0])
    if year_print != 0 and year_online != 0:
        return year_print if year_print < year_online else year_online
    else:
        return year_print if year_online == 0 else year_online
    return 0

# try to download a pdf from a given url
def get_pdf_from_url(pdf_url):
    fname = ""
    try:
        response = requests.get(pdf_url)
        content_type = response.headers['content-type']
        if not 'text' in content_type:
            #print(response.headers)
            cd= response.headers['content-disposition']
            #print(cd)
            fname = re.findall("filename=(.+)", cd)[0]
            #print(fname)
            with open('pdf_files/'+ fname +'.pdf', 'wb') as f:
                f.write(response.content)
    except:
        print("Error getting file from: ", pdf_url)
    finally:
        return fname
# add name of the pdf file for a publication record in the app database     
def set_pdf_file_value(file_name, pub_id, db_name = "app_db.sqlite3"):
    db_conn = dbh.DataBaseAdapter(db_name)
    table = 'articles'   
    done = db_conn.set_value_table(table, pub_id, "pdf_file", file_name)
    db_conn.close()
    return done

# try to get a pdf from elsevier
def get_elsevier_pdf(a_doi):
    api_key = read_keys()['elsevier']
    header = {
        'X-ELS-APIKey': api_key,
        'httpAccept': 'application/pdf'
        }
    url = f'https://api.elsevier.com/content/article/doi/{a_doi}?httpAccept=application/pdf'
    pdf_file = ""
    with requests.get(url, headers=header) as r:
        print(r.status_code)
        pdf_file = a_doi.replace('/','_')+".pdf"
        if r.status_code == 200:
            with open('pdf_files/'+pdf_file,'wb') as f:
                f.write(r.content)
    return pdf_file

# try to get a pdf from wiley
def get_wiley_pdf(a_doi):
    
    api_key = read_keys()['wiley']
    header = {
        "Wiley-TDM-Client-Token": api_key,
        'httpAccept': 'application/pdf'
        }
    pdf_url = f"https://api.wiley.com/onlinelibrary/tdm/v1/articles/{a_doi.replace('/','%2F')}?httpAccept=application/pdf"
    pdf_file = ""
    with requests.get(pdf_url, headers=header) as r:
        print(r.status_code)
        pdf_file = a_doi.replace('/','_')+".pdf"
        if r.status_code == 200:
            with open('pdf_files/'+pdf_file,'wb') as f:
                f.write(r.content)
    
    print("\t", pdf_url) 
    return pdf_file

# try to get a pdf from ACS
def get_acs_pdf(a_doi):
    pdf_url = f"https://pubs.acs.org/doi/pdf/{a_doi}?httpAccept=application/pdf"
    pdf_file = ""
    with requests.get(pdf_url) as r:
        print(r.status_code)
        pdf_file = a_doi.replace('/','_')+".pdf"
        if r.status_code == 200:
            with open('pdf_files/'+pdf_file,'wb') as f:
                f.write(r.content)
    
    print("\t", pdf_url) 
    return pdf_file

def get_not_matched_files(db_name):
    files_list = get_files_list(Path("pdf_files"))
    db_pubs = get_pub_app_data(db_name)
    missing=[]
    # check which files are really missing linking
    for file in files_list:
        found_in_db = False
        for db_pub in db_pubs:
            if file.name == db_pub[4]:
                found_in_db = True
                break
        if not found_in_db:
           missing.append(file) 
    return missing

def get_db_id(doi_value, db_name = "app_db.sqlite3"):
    db_conn = dbh.DataBaseAdapter(db_name)
    table = 'articles'   
    id_val = db_conn.get_value(table, "id", "doi", doi_value)
    db_conn.close()
    if id_val != None:
        return id_val[0]
    else:
        return 0

def get_authors_list(db_name = "app_db.sqlite3"):
    db_conn = dbh.DataBaseAdapter(db_name)
    search_in = 'authors'
    fields_required = "last_name, given_name"
    filter_str = "isap = 1"
    db_names = db_conn.get_values(search_in, fields_required, filter_str)
    db_conn.close()
    return db_names
    
# verify if statement refers to supporting data
def is_data_stmt(statement=""):
    support_keys = ["data", "underpin", "support", "result", "found", "find", "obtain", "doi","raw", "information",
                    "provide", "available", "online", "supplement"]
    count = 0
    for a_word in support_keys:
        if a_word in statement:
            count += 1
    if count > 2:
        return True
    return False

