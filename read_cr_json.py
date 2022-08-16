import gzip
import json

import csv
from pathlib import Path


# crossref data download
# D:\crosreff.archive\crossref_public_data_file_2021_01

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

def affi_in_crossref(wk):
    ukch_affiliation = False
    if 'author' in wk.keys() :
        for autr in wk['author']:
            if 'affiliation' in autr.keys():
                for affi in autr['affiliation']:
                    if "UK Catalysis Hub" in affi['name']:
                        ukch_affiliation = True
                        break
    return ukch_affiliation 


all_keys = []

for i in range(40229):
    if i>40227:
      gz_file = "D:/crosreff.archive/crossref_public_data_file_2021_01/"+ str(i) +".json.gz"
      if Path(gz_file).is_file():
        print("Looking into: ", gz_file)
        with gzip.open(gz_file, 'r') as fin:
          data = json.loads(fin.read().decode('utf-8'))
        
        print("Indexed items:", len(data['items']))
        for an_item in data['items']:
          has_award = has_affi = False
          item_keys = list(an_item.keys())
          # collect all existing CR keys
          if len(all_keys) == 0:
            all_keys = item_keys
          else:
            for a_key in item_keys:
              if not a_key in all_keys:
                all_keys.append(a_key)
          if "funder" in item_keys:
            has_award = award_in_crossref(an_item)
            if has_award:
              print (an_item['DOI'], "has award")
          if "author" in item_keys:
            has_affi = affi_in_crossref(an_item)
            if has_affi:
              print (an_item['DOI'], "has affiliation")
          if has_award or has_affi:
            art_authors = ""
            if 'author' in an_item.keys() :
                for autr in an_item['author']:
                    if 'family' in autr.keys():
                        if art_authors == "":
                            art_authors = autr['family'] + (", "+ autr ['given'] if 'given' in autr.keys() else "" )
                        else:
                            art_authors += ", " + autr['family']+ (", "+ autr ['given'] if 'given' in autr.keys() else "" )
            fund_award = ""
            if has_award:
                for fdr in an_item['funder']:
                    if 'award' in fdr.keys():
                      for awd in fdr['award']:
                          if fund_award  == "":
                              fund_award = awd
                          else:
                              fund_award += ", " +awd
            ol_year = 0
            pr_year = 0
            pub_year = 0
            if 'published-online' in an_item.keys() and 'date-parts' in an_item['published-online'].keys():
                ol_year = int(an_item['published-online']['date-parts'][0][0])
            if 'published-print' in an_item.keys() and 'date-parts' in an_item['published-print'].keys():
                pr_year = int(an_item['published-print']['date-parts'][0][0])
            if pr_year > 0 and ol_year > 0:
                if pr_year > ol_year:
                    pub_year = ol_year
                else:
                    pub_year = pr_year
            elif ol_year > 0:
                pub_year = ol_year
            elif pr_year > 0:
                pub_year = pr_year
                
            print(art_authors,"|",pub_year,"|",an_item['title'][0],
                  "|", an_item['DOI'],"|", fund_award)     
            this_pub = {}
            this_pub['authors'] = art_authors
            this_pub['year'] = pub_year
            this_pub['title'] = an_item['title'][0]
            this_pub['DOI'] = an_item['DOI']
            this_pub['award'] = fund_award 
            if has_affi:
                this_pub['with_affi'] = 1
            else:
                this_pub['with_affi'] = 0
            with open(r'cr_archive_lookup.csv', 'a', newline='',encoding='utf8') as f:
                writer = csv.writer(f)
                writer.writerow(this_pub.values())
      else:
        print("File not found")

print(all_keys)