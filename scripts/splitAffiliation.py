import csv
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()

def clear_csl():
    print("\n" *20)

def get_data(input_file, id_field):
    csv_data = {}
    fieldnames=[]
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if fieldnames==[]:
                fieldnames=list(row.keys())
            csv_data[int(row[id_field])]=row
    return csv_data, fieldnames

def get_institutions(affi_records):
    institutions = []
    for x in affi_records:
        institutions.append(affi_records[x]['Institution'].strip())
    return set(institutions)

def get_countries(affi_records):
    countries = []
    for x in affi_records:
        countries.append(affi_records[x]['Country'].strip())
    return set(countries)


def remove_breaks():
    for x in new_affi_records:
        if "affiliations" in new_affi_records[x] and "\n" in new_affi_records[x]["affiliations"]:
            new_affi_records[x]["affiliations"] = new_affi_records[x]["affiliations"].replace("\n", " ")
            print(new_affi_records[x]["affiliations"])
    with open(new_affi_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=new_affi_fields)
        writer.writeheader()
        for afi_num in new_affi_records.keys():
            writer.writerow(new_affi_records[afi_num])



def split_and_assign(input_text):
    ret_parsed = {}
    fields={'a':'ResearchGroup', 'b':'Department','c':'Faculty','d':'Institution',
            'e':'Address','f':'City','g':'Country','h':'Postcode'}
    if isinstance(input_text, str):
        user_opt = ""
        while True:
            print(input_text)
            print('Options:\n a) split\n b) assign\n selection:')
            user_opt = input()
            if user_opt in ['a', 'b']:
                break
            
        if user_opt == 'a':
            print("split separator (;,|):")
            separator = input()
            parts = input_text.split(separator)
            
            for part in parts:
               ret_parsed.update(split_and_assign(part.strip()))
        elif user_opt == 'b':
            assgnr = ""
            while True:
                if input_text.strip() in institutions_list:
                    print('assing to:', "Institution")
                    ret_parsed["Institution"] = input_text.strip()
                    break;
                elif input_text.strip() in countries_list:
                    print('assing to:', "Country")
                    ret_parsed["Country"] = input_text.strip()
                    break;
                print('Options:\n a) ResearchGroup\n b) Department\n c) Faculty\n d) Institution\n e) Address\n f) City\n g) Country\n h) Postcode')
                assgnr = input()
                print(assgnr)
                keys = list(fields.keys())
                print(keys)
                if assgnr in keys:
                    print('assing to:', assgnr, fields[assgnr])
                    ret_parsed[fields[assgnr]]=input_text.strip()
                    break;
    return ret_parsed

def get_likelu(affi_records, affi_text):
            likely_affis = {}
            for afi_key in affi_records:
                affi = affi_records[afi_key]
                matches = 0
                afi_str = ""
                for field in affi:        
                    if field != 'ID' and affi_text.find(affi[field]) != -1 \
                       and affi[field]!='':
                        matches +=1
                if matches > 2:
                    for field in affi:
                        if field != 'ID' and affi[field]!='':
                            if afi_str == "":
                                afi_str += affi[field]
                            else:
                                afi_str += ", " + affi[field]
                        similarity = similar(affi_text, afi_str)
                        likely_affis[afi_key]=[matches, similarity, afi_str]
            return likely_affis


def add_affiliation(affi_text, affi_records):
    affiliation = split_and_assign(affi_text)
    new_id = len(affi_records) + 1
    affi_records[new_id] = affiliation
    affi_records[new_id]["ID"] = new_id
    return affi_records, new_id

##text = 'University of Groningen; Engineering and Technology Institute Groningen (ENTEG), Department of Chemical Engineering; Nijenborgh 4 9747 AG Groningen The Netherlands'
##affiliation = split_and_assign(text)
##print(affiliation)

# open the affiliations and new affiliations files
affi_file = 'UKCHAffiliationsA.csv'
new_affi_file = 'UKCHAffiliations201911.csv'
links_file = "UKCHAffiliationLinksC.csv"
out_affi_file = 'UKCHAffiliationsA.csv'
out_links_file = 'UKCHAffiliationLinksC.csv'

affi_records, affi_fields = get_data(affi_file, 'ID')
new_affi_records, new_affi_fields = get_data(new_affi_file, 'ID')
links_list, link_fields = get_data(links_file, 'LinkID')

institutions_list = get_institutions(affi_records)
countries_list = get_countries(affi_records)

#remove_breaks()

counter = 0
for na_key in new_affi_records:
    counter += 1
    max_affi_id = links_list[max(links_list)]['ID']
    link_data = new_affi = new_affi_records[na_key]
    new_affis=[]
    if int(max_affi_id) < int(new_affi['ID']):
        new_affi_text = new_affi['affiliations']
        new_affis = new_affi_text.split('|')
    for affi_text in new_affis:
        affi_linked = False
        if affi_text  != "":
            likely_affis = get_likelu(affi_records, affi_text)
            clear_csl()
            print('***************************************************************')
            print(affi_text)
            if len(likely_affis) == 0:
                print("no matches")
                affi_records, new_id = add_affiliation(affi_text, affi_records)
                print('Map to ID', new_id)
                if 'affiliations' in link_data:
                    link_data.pop('affiliations')
                link_data['AffiliationID'] = new_id
                links_list[len(links_list)+1] = link_data.copy()
                affi_linked = True
            else:
                i_aff = 1
                options = {}
                max_likelu = 0
                map_id = 0
                for affi_id in likely_affis:
                    v_aff = str(affi_id) + "|"+ str(likely_affis[affi_id][0]) + str(likely_affis[affi_id][1]) + str(likely_affis[affi_id][2])
                    options[i_aff] = v_aff
                    i_aff += 1
                    if likely_affis[affi_id][1] > 0.7 and likely_affis[affi_id][1] > max_likelu:
                        map_id = affi_id
                        max_likelu = likely_affis[affi_id][1]
                if max_likelu != 0:
                    print('Map to ID', map_id)
                    if 'affiliations' in link_data:
                        link_data.pop('affiliations')
                    link_data['AffiliationID'] = map_id
                    new_link_id = len(links_list)+1
                    links_list[new_link_id] = link_data.copy()
                    affi_linked = True
                options[i_aff] = "split and add"
                usr_select = "0"
                while not affi_linked:
                    for opt in options:
                        print(opt, "Map to:", options[opt])
                    print("Selection:")
                    usr_select = int(input())
                    keys = list(options.keys())
                    if usr_select in keys:
                        print("Selected:", options[usr_select])
                        if usr_select == max(options):
                            affi_records, new_id = add_affiliation(affi_text, affi_records)
                            print('Adde ID', new_id)
                            if 'affiliations' in link_data: 
                                link_data.pop('affiliations')
                            link_data['AffiliationID'] = new_id
                            links_list[len(links_list)+1] = link_data.copy()
                            affi_linked = True
                        else:
                            map_id = options[usr_select].split("|")[0]
                            print('Map to ID', map_id)
                            if 'affiliations' in link_data:
                                link_data.pop('affiliations')
                            link_data['AffiliationID'] = map_id
                            new_link_id = len(links_list)+1
                            links_list[new_link_id] = link_data.copy()
                            affi_linked = True
                    break
                    
    if counter == 400:
        break

with open(out_affi_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=affi_fields)
    writer.writeheader()
    for afi_num in affi_records.keys():
        writer.writerow(affi_records[afi_num])
        
link_fields = new_affi_fields
link_fields.remove("affiliations")
link_fields.append("AffiliationID")
link_fields.append("LinkID")

with open(out_links_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=link_fields)
    writer.writeheader()
    for link_num in links_list.keys():
        links_list[link_num]['LinkID'] = link_num
        writer.writerow(links_list[link_num])
        
