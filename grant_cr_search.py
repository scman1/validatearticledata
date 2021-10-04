from crossref.restful import Works


def award_in_crossref(aw):
    ukch_wks =[]
   
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
    return ukch_wks

def affi_in_crossref(aw):
    ukch_wks = []
    for wk in aw:
        ukch_affiliation = False
        if 'author' in wk.keys() :
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


works = Works()
# get all the documents from 2012 which have a funder from 2012 and see if they list ukch grant numbers
pub_w_grant = works.filter(has_funder='true').filter(from_online_pub_date='2012')

ukch_grant = award_in_crossref(pub_w_grant)

foud_pubs = {}
for wk in ukch_grant:
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
    if not wk['DOI'] in foud_pubs:
         foud_pubs[wk['DOI']]= this_pub

if len(foud_pubs) > 0:
    csv_rw.write_csv_data(foud_pubs, 'cr_check_202110a.csv') 
