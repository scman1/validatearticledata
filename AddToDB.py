# Libraries
# library containign functions that read and write to csv files
import lib.handle_csv as csvh
# library for getting data from crossref
import lib.crossref_api as cr_api
# library for mapping json data
import lib.handle_json as hjson
# library for connecting to the db
import lib.handle_db as dbh


def add_affiliation(affiliation):
    affiliation, address = split_and_assign(affiliation)
    new_id = len(affi_records) + 1
    affi_records[new_id] = affiliation
    affi_records[new_id]["ID"] = new_id
    return affi_records, new_id



def db_split(affiliation):
    ret_parsed = {}
    fields={'a':'institution', 'b':'country', 'c':'department','d':'faculty',
            'e':'work_group','f':'address'}
    print (affiliation, len(affiliation))
    inst_str = dept_str = faculty_str = group_str = ctry_str = ""
    qry_where_str = ""
    addr_list=[]
    for indx in range(0, len(affiliation)):
        checking_this = affiliation[indx]['name']
        #print (affiliation[indx]['name'])
        for inst in institution_synonyms.keys():
            if inst in checking_this:
                inst_str = institution_synonyms[inst]
                checking_this = checking_this.replace(inst,'')
                break
        for inst in institutions_list:
            if inst in checking_this:
                if inst_str == "":
                    inst_str = inst
                    checking_this = checking_this.replace(inst,'')
                elif len(inst) > len(inst_str):
                    rep_str = inst.replace(inst_str, "")
                    inst_str = inst
                    checking_this = checking_this.replace(rep_str,'')
        for ctry in country_synonyms.keys():
            if ctry in checking_this:
                ctry_str = country_synonyms[ctry]
                checking_this = checking_this.replace(ctry,'')
                break
        for ctry in countries_list:
            if ctry in checking_this:
                ctry_str = inst
                checking_this = checking_this.replace(ctry,'')
                break
        for dept in department_list:
            if dept in checking_this:
                dept_str = dept
                checking_this = checking_this.replace(dept,'')
                break
        for fclty in faculty_list:
            if fclty in checking_this:
                faculty_str = fclty
                checking_this = checking_this.replace(dept,'')
                break
        for grp in group_list:
            if grp in checking_this:
                group_str = grp
                checking_this = checking_this.replace(grp,'')
                break
        checking_this = checking_this.strip()
        checking_this = checking_this.replace("  ", " ")
        addr_list.append(checking_this)
        qry_where = ""
        result=-1
        if inst_str != "":
            qry_where += "institution = '" + inst_str + "'"
            if dept_str != "":
                qry_where += " AND department = '" + dept_str + "'"
            if faculty_str != "":
                qry_where += " AND faculty = '" + faculty_str + "'"
            if group_str != "":
                qry_where += " AND group = '" + group_str + "'"
            if ctry_str != "":
                qry_where += " AND country = '" + ctry_str + "'"
            result = db_conn.get_values("affiliations","id",qry_where)
            print(result)
    print("Will Add:", ret_parsed, " with address ", addr_list)
    return ret_parsed, addr_list
    

def get_afi_id(affiliation):
    print (affiliation, len(affiliation))
    inst_str = dept_str = faculty_str = group_str = ctry_str = ""
    qry_where_str = ""
    addr_list=[]
    for indx in range(0, len(affiliation)):
        checking_this = affiliation[indx]['name']
        #print (affiliation[indx]['name'])
        if checking_this in institutions_list:
            inst_str = checking_this
        elif checking_this in department_list:
            dept_str = checking_this
        elif checking_this in faculty_list:
            faculty_str = checking_this
        elif checking_this in group_list: 
            group_str = checking_this
        elif checking_this in countries_list:
            ctry_str = checking_this
        elif checking_this in country_synonyms:
            ctry_str = country_synonyms[checking_this]
        elif checking_this in institution_synonyms:
            inst_str = institution_synonyms[checking_this]
        else:
            addr_list.append(checking_this)
    qry_where_str += "institution = '" + inst_str + "'"        
    if dept_str != "":
        qry_where_str += " AND department = '" + dept_str + "'"
    if faculty_str != "":
        qry_where_str += " AND faculty = '" + faculty_str + "'"
    if group_str != "":
        qry_where_str += " AND group = '" + group_str + "'"
    if ctry_str != "":
        qry_where_str += " AND country = '" + ctry_str + "'"
    print ('Institution:', inst_str)
    print ('Department:', dept_str)
    print ('Faculty:', faculty_str)
    print ('Group:', group_str)
    print ('Country:', ctry_str) 
    print ('Address',  addr_list)
    print (qry_where_str)
    result = db_conn.get_values("affiliations","id",qry_where_str)
    if len(result) == 1 :
        return result[0][0]
    else:
        # add new affiliation
        result = db_split(affiliation)
        

db_conn = dbh.DataBaseAdapter('ukch_articles.sqlite')

input_file = "processed_csv/AddNewArticles202002.csv"

csv_articles, _ = csvh.get_csv_data(input_file,'Num')


cr_articles = {} # Num (from CHUK), DOI, type, and other fiedls from CR.
article_columns=["Num"]
# list of article authors from cross ref
cr_authors = {} # AuthorNum, Firstname, Middle name, Last Name
author_columns = ["AuthorNum", "FirstName", "MiddleName", "LastName"]
# list of article-author links
cr_article_authour_link = {} # AuthorNum, DOI
article_authour_columns = ["DOI","AuthorNum"]


# get institutions list from affiliations table
institutions_list = db_conn.get_value_list("Affiliations", "institution")
# get coutries from affiliations table
countries_list = db_conn.get_value_list("Affiliations","country")
# get department list from affiliations table
department_list = db_conn.get_value_list("Affiliations","department")
# get faculty list from affiliations table
faculty_list = db_conn.get_value_list("Affiliations","faculty")
# get research group list from affiliations table
group_list = db_conn.get_value_list("Affiliations", "work_group")


country_synonyms = {'UK':'United Kingdom','U.K.':'United Kingdom',
                    'G.B.':'United Kingdom', "USA":"United States",
                    "U.S.A.":"United States", "China":"P. R. China",
                    "P.R.C.":"P. R. China"}
institution_synonyms = {"Paul Scherrer Institut":"Paul Scherrer Institute",
                        "PSI":"Paul Scherrer Institute",
                        "Diamond Light Source": "Diamond Light Source Ltd.",
                        "University of St Andrews": "University of St. Andrews"}


for art_num in csv_articles:
    article_title = csv_articles[art_num]['Title']
    doi_text = csv_articles[art_num]['DOI']
    
    while True:
        try_n = 1
        article_data = cr_api.getBibData(doi_text)
        if article_data != {}:
            break
        else:  
            print("****************************************************")
            print("retry", try_n, article_data)
            try_n += 1
            
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
    print("******************ARTICLE COLUMNS*******************")
    print(doi_text, article_columns)
    new_row = {}

    for key in article_columns:
        if key == 'Num':
            new_row['NumUKCH'] = art_num
        else:
            if key in article_data.keys():
                new_row[key] = hjson.jsonToPlainText(article_data[key])
    print("*******************ARTICLE DATA*********************")
    print(new_row)
    
    cr_articles[art_num] = new_row
        #print(cr_articles)
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
        #here need to create affiliation links tables
        if 'affiliation'in author.keys():
            affiliations=""
            for affl in author['affiliation']:
                affiliations += affl['name'] + "|"
            new_author['affiliations'] = affiliations
            inspected = False
            while not inspected:
                #new_title = working_file[art_num]['Title']
                print('***************************************************************')
                print('Affiliation:', affiliations)
                print('***************************************************************')
                print("Options:\n\ta) single\n\tb) multiple")
                print("selection:")
                usr_select = input()
                if usr_select == 'b':
                    #working_file[art_num]['ignore']=3 # visual inspection
                    inspected = True
                    print("parse multiple")
                elif usr_select == 'a':
                    inspected = True
                    print("parse single")
                    id = get_afi_id(author['affiliation'])
                    print("Found:",id)
            
        cr_authors[aut_num] = new_author
        art_auth_link = len(cr_article_authour_link)+1
        new_art_auth_link={}
        new_art_auth_link['DOI'] = doi_text
        new_art_auth_link['AuthorNum'] = aut_num
        cr_article_authour_link[art_auth_link] = new_art_auth_link
        
    print("********************AUTHOR DATA*********************")
    print(article_data['author'])

    # write back to a new csv file
    # create three files
    arts_file = input_file[:-4]+"Articles.csv"
    auts_file = input_file[:-4]+"Authors.csv"
    link_file = input_file[:-4]+"ArtAutLink.csv"

    csvh.write_csv_data(cr_articles, arts_file)
    csvh.write_csv_data(cr_authors, auts_file)
    csvh.write_csv_data(cr_article_authour_link, link_file)
    
