import gzip
import json

import csv
from pathlib import Path


# crossref data download
# D:\crosreff.archive\crossref_public_data_file_2021_01


def award_in_crossref(wk, award_list):
    awd_list = [] 
    for fdr in wk['funder']:
        if 'award' in fdr.keys():
           awds = 0
           for awd in fdr['award']:
               if awd in award_list: #['EP/R026939/1', 'EP/R026815/1', 'EP/R026645/1', 'EP/R027129/1', 'EP/M013219/1',
                         # 'EP/K014706/2', 'EP/K014668/1', 'EP/K014854/1', 'EP/K014714/1']:
                   awd_list.append(awd)
    return (len(awd_list) > 0)

def affi_in_crossref(wk, lookup_list):
    ukch_affiliation = ""
    if 'author' in wk.keys() :
        for autr in wk['author']:
            if 'affiliation' in autr.keys():
                for affi in autr['affiliation']:
                    for an_affi in lookup_list:
                        if 'name' in affi.keys():
                            if an_affi.lower() in affi['name'].lower(): # "UK Catalysis Hub" in affi['name']:
                                ukch_affiliation += ", " + an_affi
    return ukch_affiliation

ukch_awards_list = ['EP/R026939/1', 'EP/R026815/1', 'EP/R026645/1', 'EP/R027129/1', 'EP/M013219/1',
               'EP/K014706/2', 'EP/K014668/1', 'EP/K014854/1', 'EP/K014714/1']
ukch_affi_synonyms = ["UK Catalysis Hub"]



# opening 20100709 https://www.bbc.co.uk/news/10568048

rcah_awards_list = []
rcah_affi_synonyms = ["Research Complex at Harwell", "RCaH"]


mcc_awards = ["EP/R029431", "EP/P020194", "EP/T022213", "EP/D504872", "EP/F067496"]
# "MCC" alone does not give good results so better to keep it out
mcc_affis = ["HEC Materials Chemistry Consortium", "HEC MCC", "MCC HEC",
             "HPC MMC", "High Performance Computing MMC", "High End Computing MMC",
             "UK Materials and Molecular Modelling Hub", "MMM Hub",
             "Materials Chemistry Consortium", "CoSeC",
             "Computational Science Centre for Research Communities",
             "HPCx resources", "HECToR"]


isis_awards =[]
isis_synonyms=['ISIS', 'ISIS Facility', 'ISIS Neutron and Muon Source', 'ISIS STFC', 'STFC ISIS']

awards_list = ukch_awards_list + rcah_awards_list + mcc_awards
affis_list = ukch_affi_synonyms + rcah_affi_synonyms + mcc_affis

awards_list = isis_awards
affis_list = isis_synonyms

print("Awards:", awards_list, "\n Affiliations", affis_list)

all_keys = []

for i in range(26810):
    if i>0:
      gz_file = "D:/crosreff.archive/crossref_public_data_file_2022_04/"+ str(i) +".json.gz"
      if Path(gz_file).is_file():
        print("Looking into: ", gz_file)
        with gzip.open(gz_file, 'r') as fin:
          data = json.loads(fin.read().decode('utf-8'))
        print("Indexed items:", len(data['items']))
        for an_item in data['items']:
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
          if pub_year > 1984:
            has_award = False
            has_affi =  ""
            item_keys = list(an_item.keys())
            # collect all existing CR keys
            all_keys = list(set(all_keys).union(set(item_keys)))
             
            if "funder" in item_keys:
              has_award = award_in_crossref(an_item, awards_list)
              if has_award:
                print (an_item['DOI'], "has award")
            if "author" in item_keys:
              has_affi = affi_in_crossref(an_item, affis_list)
              if has_affi != "" :
                print (an_item['DOI'], "affi found", has_affi)
            if has_award or has_affi != "":
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
            
                
              print(art_authors,"|",pub_year,"|",an_item['title'][0],
                    "|", an_item['DOI'],"|", fund_award)     
              this_pub = {}
              this_pub['authors'] = art_authors
              this_pub['year'] = pub_year
              this_pub['title'] = an_item['title'][0]
              this_pub['DOI'] = an_item['DOI']
              this_pub['award'] = fund_award 
              this_pub['with_affi'] = has_affi
              this_pub['found_at'] = Path(gz_file).name
                 
              with open(r'cr_archive_lookup_202208ISIS.csv', 'a', newline='',encoding='utf8') as f:
                  writer = csv.writer(f)
                  writer.writerow(this_pub.values())
      else:
        print("File not found")

print(all_keys)
