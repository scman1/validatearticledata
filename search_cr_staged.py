# Connecting to the db
import lib.handle_db as dbh

# read and write csv files
import lib.handle_csv as csv_rw

# date functions
from datetime import datetime, date, timedelta

#CR libraries
from crossref.restful import Works, Etiquette

# search for UKCH Awards in CR record
def award_in_crossref(aw):
    ukch_wks =[]
    not_revised = []
    for wk in aw:      
        awd_list = []
        if 'funder' in wk.keys():
            for fdr in wk['funder']:
                if 'award' in fdr.keys():
                   awds = 0
                   for awd in fdr['award']:
                        if awd in ['EP/R026939/1', 'EP/R026815/1', 'EP/R026645/1', 'EP/R027129/1', 'EP/M013219/1',
                                  'EP/K014706/2', 'EP/K014668/1', 'EP/K014854/1', 'EP/K014714/1']:
                            awd_list.append(awd)
                            #print (fdr)
                            break
        else:
            not_revised.append(wk)
        if len(awd_list) > 0:
            ukch_wks.append(wk)
    return ukch_wks, not_revised

def collect_keys(aw, wk_keys):
    for wk in aw:
        these_keys = wk.keys()
        for a_key in these_keys:
            if a_key in wk_keys:
                wk_keys[a_key] += 1
            else:
                wk_keys[a_key] = 1
    return wk_keys

def collect_fdr_keys(aw, wk_keys):
    for wk in aw:
        if 'funder' in wk.keys():
            for fdr in wk['funder']:
                these_keys = fdr.keys()
                for a_key in these_keys:
                    if a_key in wk_keys:
                        wk_keys[a_key] += 1
                    else:
                        wk_keys[a_key] = 1
    return wk_keys

def collect_awds(aw, wk_keys):
    for wk in aw:
        if 'funder' in wk.keys():
            for fdr in wk['funder']:
                if 'award' in fdr.keys():
                   awds = 0
                   for awd in fdr['award']:
                        if awd in wk_keys:
                            wk_keys[awd] += 1
                        else:
                            wk_keys[awd] = 1
    return wk_keys

# search for UKCH Affiliation in CR record
def affi_in_crossref(aw):
    ukch_wks = []
    for wk in aw:
        ukch_affiliation = False
        if 'author' in wk.keys():
            for autr in wk['author']:
                if 'affiliation' in autr.keys():
                    for affi in autr['affiliation']:
                        if "UK Catalysis Hub" in affi['name']:
                            ukch_affiliation = True
                            break
                    if ukch_affiliation:
                        ukch_wks.append(wk)
                        break
    return  ukch_wks
    
my_etiquette = Etiquette('UK Catalysis Hub Catalysis Data Infrastructure', 'Prototype 1', 'https://ukcatalysishub.co.uk/core/', 'nievadelahidalgaa@cardiff.ac.uk')


works = Works(etiquette=my_etiquette)

start_date = date(2022, 4, 1)
end_date = date(2022, 4, 1)

pubs_with_award = []
skiped_works =[]
wk_keys = {}
fd_keys = {}
awds_lst = {}
while end_date < datetime.now().date():
    end_date = start_date + timedelta(days=7)
    print ("From:", str(start_date), "to",  str(end_date))
    # works with from_published_date and until_published_date 
    # next test with from_deposit_date and until_deposit_date
    # Valid filters for this route are: alternative_id, archive, article_number, assertion, assertion-group, 
    #    award.funder, award.number, category-name, clinical-trial-number, container-title, content-domain,
    #    directory, doi, from-accepted-date, from-created-date, from-deposit-date, from-event-end-date,
    #    from-event-start-date, from-index-date, from-issued-date, from-online-pub-date, from-posted-date,
    #    from-print-pub-date, from-pub-date, from-update-date, full-text.application, full-text.type, 
    #    full-text.version, funder, funder-doi-asserted-by, group-title, has-abstract, has-affiliation,
    #    has-archive, has-assertion, has-authenticated-orcid, has-award, has-clinical-trial-number,
    #    has-content-domain, has-domain-restriction, has-event, has-full-text, has-funder, has-funder-doi,
    #    has-license, has-orcid, has-references, has-relation, has-update, has-update-policy, is-update, 
    #    isbn, issn, license.delay, license.url, license.version, location, member, orcid, prefix,
    #    relation.object, relation.object-type, relation.type, type, type-name, until-accepted-date,
    #    until-created-date, until-deposit-date, until-event-end-date, until-event-start-date,
    #    until-index-date, until-issued-date, until-online-pub-date, until-posted-date,
    #    until-print-pub-date, until-pub-date, until-update-date, update-type, updates

    print(works.filter(has_funder='true').filter(from_deposit_date=str(start_date)).filter(until_deposit_date=str(end_date)).url)
    pub_w_grant = works.filter(has_funder='true').filter(from_deposit_date=str(start_date)).filter(until_deposit_date=str(end_date))
    
    aw, _  = award_in_crossref(pub_w_grant)
    ukch_wks = []
    
    for wk in aw:     
        
        awd_list = [] 
        for fdr in wk['funder']:
            if 'award' in fdr.keys():
               awds = 0
               for awd in fdr['award']:
                   if awd in ['EP/R026939/1', 'EP/R026815/1', 'EP/R026645/1', 'EP/R027129/1', 'EP/M013219/1',
                              'EP/K014706/2', 'EP/K014668/1', 'EP/K014854/1', 'EP/K014714/1']:
                       awd_list.append(awd)
        if len(awd_list) > 0:
            ukch_wks.append(wk)
    
    foud_pubs = {}
    if len(ukch_wks) > 0:
        foud_pubs = {}
        for wk in ukch_wks:
            art_authors = ""
            if 'author' in wk.keys() :
                for autr in wk['author']:
                    if art_authors == "":
                        art_authors = autr['family']+", " + (", "+ autr ['given'] if 'given' in autr.keys() else "" )
                    else:
                        art_authors += ", " + autr['family']+ (", "+ autr ['given'] if 'given' in autr.keys() else "" )
            fund_award = ""
            for fdr in wk['funder']:
                if 'award' in fdr.keys():
                  for awd in fdr['award']:
                       if awd in ['EP/R026939/1', 'EP/R026815/1', 'EP/R026645/1', 'EP/R027129/1', 'EP/M013219/1',
                                  'EP/K014706/2', 'EP/K014668/1', 'EP/K014854/1', 'EP/K014714/1']:
                            if fund_award  == "":
                                fund_award = awd
                            else:
                                fund_award += ", " +awd

            ol_year = 0
            pr_year = 0
            pub_year = 0
            if 'published-online' in wk.keys() and 'date-parts' in wk['published-online'].keys():
                ol_year = int(wk['published-online']['date-parts'][0][0])
            if 'published-print' in wk.keys() and 'date-parts' in wk['published-print'].keys():
                pr_year = int(wk['published-print']['date-parts'][0][0])
            if pr_year > 0 and ol_year > 0:
                if pr_year > ol_year:
                    pub_year = ol_year
                else:
                    pub_year = pr_year
            elif ol_year > 0:
                pub_year = ol_year
            elif pr_year > 0:
                pub_year = pr_year

            print(art_authors,"|",pub_year,"|",wk['title'][0],
                  "|", wk['DOI'],"|", fund_award)     
            this_pub = {}
            this_pub['authors'] = art_authors
            this_pub['year'] = pub_year
            this_pub['title'] = wk['title'][0]
            this_pub['DOI'] = wk['DOI']
            this_pub['awards'] = fund_award
            if not wk['DOI'] in foud_pubs:
                 foud_pubs[wk['DOI']]= this_pub

        
        # WRITE TO FILE
        if len(foud_pubs) > 0:
            csv_rw.write_csv_data(foud_pubs, 'cr_search_'+str(end_date)+'.csv') 
        
    start_date = end_date + timedelta(days=1)