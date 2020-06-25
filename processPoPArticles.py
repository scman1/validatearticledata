# rewrite using modules
# looking up new references from PoP

# Libraries
# library containign functions that read and write to csv files
import lib.handle_csv as csvh
import lib.handle_db as dbh
import lib.text_comp as txtc
import lib.crossref_api as cr_api
import lib.handle_urls as urlh

from pathlib import Path


# input files
new_results_file = 'pop_searches/PoPCites20200624.csv'
previous_results = 'pop_searches/ukch_pop_2VT.csv'

#output files
nr_wf = new_results_file[:-4]+"_wf.csv"
working_filem = wf_fields = None
current_pass = 0
if Path(nr_wf).is_file():
    working_file, wf_fields = csvh.get_csv_data(nr_wf,'Num')
    for art_num in working_file:
        if current_pass < int(working_file[art_num]['ignore']) :
            current_pass = int(working_file[art_num]['ignore'])

print("Started:", nr_wf)

if not Path(nr_wf).is_file():
    csv_articles, fn_articles = csvh.get_csv_data(new_results_file,'Num')
    prev_articles, fn_prev = csvh.get_csv_data(previous_results,'Num')
    # pass 1a exact match
    for art_num in csv_articles:
        new_title = csv_articles[art_num]['Title']
        for prev_num in prev_articles:
            prev_articles[prev_num]['Title']
            if new_title == prev_articles[prev_num]['Title']:
                #print(art_num, 'Title:', csv_articles[art_num]['Title'], "already processed", prev_num, prev_articles[prev_num]['Title'])
                csv_articles[art_num]['ignore']=1
            break
        if not 'ignore' in csv_articles[art_num].keys():
            csv_articles[art_num]['ignore']=0
    # pass 1b approximate match
    for art_num in csv_articles:
        if csv_articles[art_num]['ignore']==0:
            new_title = csv_articles[art_num]['Title']
            for prev_num in prev_articles:
                if txtc.similar(new_title, prev_articles[prev_num]['Title'])> 0.80:
                    #print(art_num, 'Title:', csv_articles[art_num]['Title'], "already processed", prev_num, prev_articles[prev_num]['Title'])
                    csv_articles[art_num]['ignore']=1
                    break
    csvh.write_csv_data(csv_articles, nr_wf)
        
if current_pass > 0 and current_pass < 2:
    print("pass 2")
    # pass 2
    # check titles for likelihood of being catalysis articles using keywords from titles in current DB 
    print("Get word list from DB")
    x = dbh.DataBaseAdapter('ukch_articles.sqlite')
    db_titles = x.get_value_list('articles','title')
    title_words = set()
    ignore_words=set(['the','of','to','and','a','in','is','it', 'their', 'so', 'as'])
    average = 0
    words_sum = 0.0
    for title in db_titles:
        one_title = set(title.lower().split())
        one_title = one_title - ignore_words
        title_words = title_words.union(one_title)
        words_sum += len(one_title) 
        
    average = words_sum /len(db_titles)
    print("Average words per title:", average)
    title_words = title_words - ignore_words
    for art_num in working_file:
        if 0 == int(working_file[art_num]['ignore']):
            art_title = working_file[art_num]['Title']
            art_words = set(art_title.lower().split())
            occurrences = len(title_words.intersection(art_words))
            if occurrences <= 4:
                print("occurrences:", occurrences, "in title:", art_title)
                working_file[art_num]['ignore']=2
            else:
                print("occurrences:", occurrences, "in title:", art_title)
    csvh.write_csv_data(working_file, nr_wf)

if current_pass == 2:
    print("still pass 2")
    i = 0
    for art_num in working_file:
        #print('Title:', working_file[art_num]['Title'],working_file[art_num]['ignore'])
        if working_file[art_num]['ignore']=='0':
            inspected = False
            while not inspected:
                new_title = working_file[art_num]['Title']
                print('Title:', working_file[art_num]['Title'])
                print('***************************************************************')
                print("Oprions:\n\ta) add\n\tb) ignore")
                print("selection:")
                usr_select = input()
                if usr_select == 'b':
                    working_file[art_num]['ignore']=3 # visual inspection
                    inspected = True
                elif usr_select == 'a':
                    inspected = True
            i += 1
    print("To Process:", i, "Pass:", current_pass)
    csvh.write_csv_data(working_file, nr_wf)

if current_pass == 3:
    print("pass 3")
    i = 0
    for art_num in working_file:
        if working_file[art_num]['ignore']=='0':
            new_title = working_file[art_num]['Title']
            new_doi = cr_api.getDOIForTitle(new_title)
            if new_doi == "":
                print("Missing DOI:", new_title)
                working_file[art_num]['ignore'] = '4' # could check later to see if thesis or book
                i +=1
            else:
                print("DOI found:", new_doi, "for:", new_title)
                working_file[art_num]['DOI'] = new_doi
                working_file[art_num]['ignore'] = '0'
    print("without DOI:", i)
    csvh.write_csv_data(working_file, nr_wf)
            
if current_pass == 4:
    print("Pass 4")
    i = 0
    db_conn = dbh.DataBaseAdapter('ukch_articles.sqlite')
    for art_num in working_file:
        if working_file[art_num]['ignore']=='0':
            new_title = working_file[art_num]['Title']
            new_doi = working_file[art_num]['DOI']
            db_title = db_conn.get_value("articles", "title", "doi", new_doi)
            if db_title == None:
                print("Not in DB:", new_doi, new_title)
            else:
                print("Already in DB:", new_doi, "for:", new_title, db_title)
                working_file[art_num]['ignore'] = '5'
    print("without DOI:", i)
    csvh.write_csv_data(working_file, nr_wf)

if current_pass == 5:
    print("Pass 5")
    i = 0
    for art_num in working_file:
        if working_file[art_num]['ignore']=='0':
            article_title = working_file[art_num]['Title']
            article_doi = working_file[art_num]['DOI']
            article_url =working_file[art_num]['ArticleURL']
            print("Analysing:", article_title, article_doi, article_url)
            # try to retrive html page for article using link from crossref first
            # and if not try url from pop
            # find reference to uk catalysis hub in html text
            # if found mark as relevant
            found = ""
            referents = ["uk catalysis hub", "uk catalysis", "catalysis hub",
                 'EP/R026645/1', 'resources', 'EP/K014668/1', 'EPSRC', 'EP/K014714/1',
                 'Hub','provided', 'grant', 'biocatalysis', 'EP/R026815/1', 'EP/R026939/1',
                 'support', 'membership', 'EP/M013219/1', 'UK', 'kindly', 'Catalysis',
                 'funded', 'EP/R027129/1', 'Consortium', 'thanked', 'EP/K014854/1', 'EP/K014706/2']
            
            found = urlh.findFromDOI(article_title, article_doi, referents)
            working_file[art_num]['checked_doi'] = 1
            working_file[art_num]['ack_doi'] = found
            found = urlh.findFromURI(article_title, article_url, referents)
            working_file[art_num]['checked_url'] = 1
            working_file[art_num]['ack_url'] = found
            print("Ack:", found)
    csvh.write_csv_data(working_file, nr_wf)

