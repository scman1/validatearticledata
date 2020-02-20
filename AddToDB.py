# Libraries
# library containign functions that read and write to csv files
import lib.handle_csv as csvh
# library for getting data from crossref
import lib.crossref_api as cr_api


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

input_file = "pop_searches/AddNewArticles202002.csv"

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
        article_data = cr_api.getBibData(doi_text)
        print("****************************************************")
        print(article_data)
        if article_data != {}:
            break
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
    print(doi_text, article_columns)
    new_row = {}

    for key in article_columns:
        if key == 'Num':
            new_row['NumUKCH'] = art_num
        else:
            if key in article_data.keys():
                new_row[key] = jsonToPlainText(article_data[key])

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
    print(article_data['author'])
