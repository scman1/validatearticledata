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

def get_working_file_data(new_rfile):
    #output files
    nr_wf = new_rfile[:-4]+"_wf.csv"
    working_file = wf_fields = None
    current_pass = 0
    if Path(nr_wf).is_file():
        working_file, wf_fields = csvh.get_csv_data(nr_wf)
        for art_num in working_file:
            if current_pass < int(working_file[art_num]['ignore']) :
                current_pass = int(working_file[art_num]['ignore'])

    print("Started:", nr_wf)
    return nr_wf, working_file, wf_fields, current_pass

def check_previous_results (new_results_file, previous_results, nr_wf):
    csv_articles, fn_articles = csvh.get_csv_data(new_results_file)
    prev_articles, fn_prev = csvh.get_csv_data(previous_results)
    # pass 1a exact match
    for art_num in csv_articles:
        new_id = csv_articles[art_num]['UT (Unique WOS ID)']
        for prev_num in prev_articles:
            if new_id == prev_articles[prev_num]['wos_ID']:
                #print(art_num, 'Title:', csv_articles[art_num]['Title'], "already processed", prev_num, prev_articles[prev_num]['Title'])
                csv_articles[art_num]['ignore']=1
            break
        if not 'ignore' in csv_articles[art_num].keys():
            csv_articles[art_num]['ignore']=0
    # pass 1b approximate match
    for art_num in csv_articles:
        if csv_articles[art_num]['ignore']==0:
            new_title = csv_articles[art_num]['Article Title']
            for prev_num in prev_articles:
                if txtc.similar(new_title, prev_articles[prev_num]['Article Title'])> 0.80:
                    csv_articles[art_num]['ignore']=1
                    break
    csvh.write_csv_data(csv_articles, nr_wf)
    return 1

def get_title_word_list(db_name):
    x = dbh.DataBaseAdapter(db_name)
    db_titles = x.get_value_list('articles','title')
    title_words = set()
    ignore_words=set(['the','of','to','and','a','in','is','it', 'their', 'so', 'as', 'an','for'])
    average = 0
    words_sum = 0.0
    for title in db_titles:
        one_title = set(title.lower().split())
        one_title = one_title - ignore_words
        remove_w = set()
        add_w = set()
        for a_word in one_title:
            new_word = "".join(filter(str.isalnum, a_word))
            if new_word != a_word:
                remove_w.add(a_word)
                add_w.add(new_word)        
        one_title = one_title - remove_w
        one_title = one_title.union(add_w)
        
        title_words = title_words.union(one_title)
        words_sum += len(one_title) 
        
    average = words_sum /len(db_titles)
    print("Average words per title:", average)

    title_words = title_words - ignore_words

    print (f"Words used for titles {len(title_words)}")
    return title_words

def check_title_similarity(working_file, db_name, nr_wf):
    # check titles for likelihood of being catalysis articles using keywords from titles in current DB 
    print("Get title word list from DB")
    title_words = get_title_word_list(db_name)

    for art_num in working_file:
        if 0 == int(working_file[art_num]['ignore']):
            art_title = working_file[art_num]['Article Title']
            art_words = set(art_title.lower().split())
            occurrences = len(title_words.intersection(art_words))
            print("occurrences:", occurrences, "in title:", art_title)
            if occurrences <= 4:
                working_file[art_num]['ignore']=2
    csvh.write_csv_data(working_file, nr_wf)
    print(title_words)
    return 2

def mark_non_articles(article_data, nr_wf):
    for art_num in article_data:
        if 0 == int(article_data[art_num]['ignore']):
            if "Article" != article_data[art_num]['Document Type']:
                article_data[art_num]['ignore']=3
    csvh.write_csv_data(article_data, nr_wf)
    return 3     
            
def mark_in_db(working_file, db_name, nr_wf):
    x = dbh.DataBaseAdapter(db_name)
    db_dois = x.get_value_list('articles','doi')
    for art_num in working_file:
        if 0 == int(working_file[art_num]['ignore']):
            art_doi = working_file[art_num]['DOI']
            if art_doi in db_dois:
                working_file[art_num]['ignore']=4
    csvh.write_csv_data(working_file, nr_wf)
    return 4

def check_referents(working_file, nr_wf):
    referents = ["uk catalysis hub", "uk catalysis", "catalysis hub",
                 'EP/R026645/1', 'EP/K014668/1', 'EP/K014714/1',
                 'EP/R026815/1', 'EP/R026939/1', 'EP/M013219/1', 'EP/R027129/1',
                 'EP/K014854/1', 'EP/K014706/2']
    ref_fields = ["Addresses","Affiliations", "Funding Orgs", "Funding Name Preferred",
                  "Funding Text"]
    
    for art_num in working_file:
        for a_rfield in ref_fields:
            ref_text = working_file[art_num][a_rfield]
            for a_referent in referents:
                if a_referent in ref_text:
                    print("found reference in ", ref_text)
                    working_file[art_num]['ack']=1
                    break            
            if not 'ack' in working_file[art_num].keys():
                working_file[art_num]['ack']=0
                
    csvh.write_csv_data(working_file, nr_wf)
    return 5

def start_processing(new_rfile, prev_r_file, db_name):
    processing_idx = 0
    wf_name, wf_data, wf_fields, processing_idx = get_working_file_data(new_rfile)
    print (f"Current processing stage is {processing_idx}")
    if processing_idx == 0:
        print("Nothing has been processed start by comparing to previous results")
        processing_idx = check_previous_results(new_rfile, prev_r_file, wf_name)
    if processing_idx == 1:
        print(f"Check if titles could be UKCH titles in db {db_name}")
        processing_idx = check_title_similarity(wf_data, db_name, wf_name)
    if processing_idx == 2:
        print(f"Ignore non-article entries")
        processing_idx = mark_non_articles(wf_data, wf_name)
    if processing_idx == 3:
        print(f"Ignore articles in db")
        processing_idx = mark_in_db(wf_data, db_name, wf_name)
    if processing_idx == 4:
        print(f"Check referents (ack, grant, affiliation)")
        processing_idx = check_referents(wf_data, wf_name)
        
    
if __name__ == '__main__':
    # input files
    new_results_file = 'WebOfScience/wos_202401/savedrecs_2013-2024.csv'
    previous_results = 'WebOfScience/wos_202311/wos_202311_ukch_db.csv'
    current_db = "db_files/production.sqlite3"
    start_processing(new_results_file, previous_results, current_db)
    

