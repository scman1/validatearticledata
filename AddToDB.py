# Libraries
# library containign functions that read and write to csv files
import lib.handle_csv as csvh
# library for getting data from crossref
import lib.crossref_api as cr_api
import lib.handle_json as hjson


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
                    prin("parse single")
            
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
    
