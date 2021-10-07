from crossref.restful import Works

import csv

def award_in_crossref(wk):
    
    awd_list = [] 
    for fdr in wk['funder']:
        if 'award' in fdr.keys():
           awds = 0
           for awd in fdr['award']:
               if awd in ['EP/R026939/1', 'EP/R026815/1', 'EP/R026645/1', 'EP/R027129/1', 'EP/M013219/1',
                          'EP/K014706/2', 'EP/K014668/1', 'EP/K014854/1', 'EP/K014714/1']:
                   awd_list.append(awd)
    return (len(awd_list) > 0)

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
pyear = '2015'
pub_w_grant = works.filter(has_funder='true').filter(has_award='true').filter(from_pub_date=pyear).filter(until_pub_date=pyear)

#ukch_grant = award_in_crossref(pub_w_grant)

foud_pubs = {}
counter = 0
for wk in pub_w_grant:
    counter +=1
    has_award = award_in_crossref(wk)
    print("{:09d}".format(counter), "DOI: ", wk['DOI'], "Has award", has_award)     
    if has_award:
        art_authors = ""
        if 'author' in wk.keys() :
            for autr in wk['author']:
                if 'family' in autr.keys():
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
        this_pub['award'] = fund_award 
      
        with open(r'name_'+pyear+'.csv', 'a', newline='',encoding='utf8') as f:
            writer = csv.writer(f)
            writer.writerow(this_pub.values())
