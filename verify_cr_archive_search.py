import gzip
import json

import csv
from pathlib import Path


# crossref data download
# D:\crosreff.archive\crossref_public_data_file_2021_01


def get_crossref_affis(wk, lookup_list):
    ukch_affiliation = ""
    if 'author' in wk.keys() :
        for autr in wk['author']:
            if 'affiliation' in autr.keys():
                for affi in autr['affiliation']:
                    for an_affi in lookup_list:
                        if 'name' in affi.keys():
                            if an_affi.lower() in affi['name'].lower(): # "UK Catalysis Hub" in affi['name']:
                                ukch_affiliation += ", " + affi['name']
    return ukch_affiliation

# set name of file to verify
check_file = r'cr_archive_lookup_202208MCC_only.csv'
out_file = r'cr_archive_lookup_202208MCC_onlyRev.csv'

with open(check_file, newline='',encoding='utf8') as f:
    reader = csv.reader(f)
    new_gz_file = ""
    data = None
    for row in reader:
        print(row)
        affis = ""
        pub_doi =  row[3]
        affis_list = list(set(row[5].split(', ')))
        file_name =  row[6]
        
        if new_gz_file != file_name:
            new_gz_file = file_name
            gz_file = "D:/crosreff.archive/crossref_public_data_file_2022_04/"+ file_name
            if Path(gz_file).exists():
                print("Looking into: ", gz_file)
                with gzip.open(gz_file, 'r') as fin:
                    data = json.loads(fin.read().decode('utf-8'))
        if data != None:
            for an_item in data['items']:
                if pub_doi == an_item['DOI']:
                    affis = get_crossref_affis(an_item, affis_list)
                    print(affis)
                    break
        this_pub = {}
        this_pub['authors'] = row[0]
        this_pub['year'] = row[1]
        this_pub['title'] = row[2]
        this_pub['DOI'] = row[3]
        this_pub['award'] = row[4]
        this_pub['sysnonim'] = row[5]
        this_pub['location'] = row[6]
        this_pub['affiliation'] = affis
        this_pub['OK'] = row[8]
        this_pub['num'] = row[9]
        
        with open(out_file, 'a', newline='',encoding='utf8') as f:
            writer = csv.writer(f)
            writer.writerow(this_pub.values())

