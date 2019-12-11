import csv
import datetime
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

def get_institutions(affi_records, new_affi_records):
    institutions = []
    for x in affi_records:
        institutions.append(affi_records[x]['Institution'].strip())
    for x in new_affi_records:
        institutions.append(new_affi_records[x]['Institution'].strip())
    return list(set(institutions))

def get_countries(affi_records, new_affi_records):
    countries = []
    for x in affi_records:
        countries.append(affi_records[x]['Country'].strip())
    for x in new_affi_records:
        countries.append(new_affi_records[x]['Country'].strip())
    return list(set(countries))

def get_values(affi_records, new_affi_records, val_field):
    value_list = []
    for x in affi_records:
        if val_field in affi_records[x]:
            value_list.append(affi_records[x][val_field].strip())
    for x in new_affi_records:
        value_list.append(new_affi_records[x][val_field].strip())
    return list(set(value_list))

def get_addresses(new_affi_records, addr_fields):
    addresses=[]
    for x in new_affi_records:
        for addr_field in addr_fields:
            if new_affi_records[x][addr_field].strip() != "":
                addresses.append(new_affi_records[x][addr_field].strip())
    return list(set(addresses))

def get_affi_vector():
    affi_vector = { 'c':["Country", False], 'd':["Department", False],
                    'f':["Faculty", False], 'g':["Group", False],
                    'i':["Institution", False], 'u':["Unit", False]} 
    return affi_vector

def remove_last_bar():
    for x in new_affi_records:
        if int(new_affi_records[x]["aff_num"]) > 1:
            affs_text = new_affi_records[x]["affiliations"]
            len_aff_txt = len(affs_text)
            new_affi_records[x]["affiliations"] = affs_text[0:len_aff_txt-1]
    new_affi_fields.append("aff_num")
    with open(out_new_affi_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=new_affi_fields)
        writer.writeheader()
        for afi_num in new_affi_records.keys():
            writer.writerow(new_affi_records[afi_num])

def split_affiliations():
    new_id = max(new_affi_records)
    new_list = {}
    for x in new_affi_records:
        if int(new_affi_records[x]["aff_num"]) > 0:
            affs_text = new_affi_records[x]["affiliations"]
            affs_list = affs_text.split("|")
            aff_count = 0
            print("List:", affs_text)
            for ind_affi_text in affs_list:
                if aff_count == 0:
                    print("  *" ,x, ind_affi_text)
                    new_affi_records[x]["affiliations"] = ind_affi_text
                    aff_count += 1
                else:
                    new_id +=1
                    print("  *" , new_id , ind_affi_text)
                    new_record = new_affi_records[x].copy()
                    new_record["affiliations"] = ind_affi_text
                    new_list[new_id] = new_record
    print(len(new_list))
    new_affi_records.update(new_list)
    with open(out_new_affi_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=new_affi_fields)
        writer.writeheader()
        for afi_num in new_affi_records.keys():
            writer.writerow(new_affi_records[afi_num])

def count_affiliations():
    for x in new_affi_records:
        new_affi_records[x]["aff_num"] = new_affi_records[x]["affiliations"].count("|")
    new_affi_fields.append("aff_num")
    with open(out_new_affi_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=new_affi_fields)
        writer.writeheader()
        for afi_num in new_affi_records.keys():
            writer.writerow(new_affi_records[afi_num])

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
start = datetime.datetime.now().time()
interactions = 0
affi_file = 'UKCHAffiliationsA.csv'
new_affi_file = 'UKCHAffiliations201911M.csv'
out_new_affi_file = 'UKCHAffiliations201911M.csv'
links_file = "UKCHAffiliationLinksC.csv"
out_affi_file = 'UKCHAffiliationsA.csv'
out_links_file = 'UKCHAffiliationLinksC.csv'

affi_records, affi_fields = get_data(affi_file, 'ID')
new_affi_records, new_affi_fields = get_data(new_affi_file, 'AffiLinkID')
links_list, link_fields = get_data(links_file, 'LinkID')



#remove_breaks()
#count_affiliations()
#remove_last_bar()
#count_affiliations()
#split_affiliations()
#count_affiliations()

affi_fields = ['Affi0', 'Affi1', 'Affi2', 'Affi3', 'Affi4', 'Affi5', 'Affi6', 'Affi7']
addr_fields = ['Add01','Add02','Add03','Add04','Add05']
addresses_list = get_addresses(new_affi_records, addr_fields)

institutions_list = get_institutions(affi_records, new_affi_records)
countries_list = get_countries(affi_records, new_affi_records)
departments_list = get_values(affi_records, new_affi_records, "Department")
faculties_list = get_values(affi_records, new_affi_records, "Faculty")
researchgroups_list = get_values(affi_records, new_affi_records, "Group")
units_list= get_values(affi_records, new_affi_records, "Unit")

counter = 0
for na_key in new_affi_records:
    if new_affi_records[na_key]['processed'] != "1":
        counter += 1
        addr_index = 0
        affi_text = new_affi_records[na_key]['affiliations']
        affi_vector = get_affi_vector()
        for afi_field in affi_fields:
            val = new_affi_records[na_key][afi_field]
            if val != "":
                if val in institutions_list:
                    new_affi_records[na_key]["Institution"] = val
                    affi_vector['i'][1] = True
                elif val in countries_list:
                    new_affi_records[na_key]["Country"] = val
                    affi_vector['c'][1] = True
                elif val in departments_list:
                    new_affi_records[na_key]["Department"] = val
                    affi_vector['d'][1] = True
                elif val in faculties_list:
                    new_affi_records[na_key]["Faculty"] = val
                    affi_vector['f'][1] = True
                elif val in researchgroups_list:
                    new_affi_records[na_key]["Group"] = val
                    affi_vector['g'][1] = True
                elif val in units_list:
                    new_affi_records[na_key]["Unit"] = val
                    affi_vector['u'][1] = True
                elif val in addresses_list:
                    new_affi_records[na_key][addr_fields[addr_index]] = val
                    addr_index += 1    
                else:
                #Not found, assign manually
                    interactions += 1
                    val_linked = False
                    fields_to_assign = ['a']
                    for selector in affi_vector:
                        if affi_vector[selector][1] == False:
                           fields_to_assign.append(selector)
                    while not val_linked:
                        print('***************************************************************')
                        print(affi_text)
                        print('Assign:', val,"to:")
                        for key in affi_vector:
                            if not affi_vector[key][1]:
                                print(key,"-" , affi_vector[key][0])
                        print("a","-" , "Address")
                        print("Selection:")
                        usr_select = input()
                        if usr_select in fields_to_assign:
                            if usr_select == "a":
                                new_affi_records[na_key][addr_fields[addr_index]] = val
                                addresses_list.append(val)
                                addr_index += 1
                            else:
                                new_affi_records[na_key][affi_vector[usr_select][0]] = val
                                affi_vector[usr_select][1] = True
                                if affi_vector[usr_select][0] == 'Country':
                                    countries_list.append(val)    
                                elif affi_vector[usr_select][0] == 'Institution':
                                    institutions_list.append(val)
                                elif affi_vector[usr_select][0] == 'Department':
                                    departments_list.append(val)
                                elif affi_vector[usr_select][0] == 'Faculty':
                                    faculties_list.append(val)
                                elif affi_vector[usr_select][0] == 'Group':
                                    researchgroups_list.append(val)
                            val_linked = True
        if counter == 500:
            print("start:", start, "end", datetime.datetime.now().time(), \
                  "interactions:", interactions, "records", counter)
            break


for key in new_affi_records:
    for field in new_affi_records[key].keys():
        if not field in new_affi_fields:
            new_affi_fields.append(field)

with open(out_new_affi_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=new_affi_fields)
    writer.writeheader()
    for afi_num in new_affi_records.keys():
        writer.writerow(new_affi_records[afi_num])





    
##    max_affi_id = links_list[max(links_list)]['ID']
##    link_data = new_affi = new_affi_records[na_key]
##    new_affis=[]
##    if int(max_affi_id) < int(new_affi['ID']):
##        new_affi_text = new_affi['affiliations']
##        new_affis = new_affi_text.split('|')
##    for affi_text in new_affis:
##        affi_linked = False
##        if affi_text  != "":
##            likely_affis = get_likelu(affi_records, affi_text)
##            clear_csl()
##            print('***************************************************************')
##            print(affi_text)
##            if len(likely_affis) == 0:
##                print("no matches")
##                affi_records, new_id = add_affiliation(affi_text, affi_records)
##                print('Map to ID', new_id)
##                if 'affiliations' in link_data:
##                    link_data.pop('affiliations')
##                link_data['AffiliationID'] = new_id
##                links_list[len(links_list)+1] = link_data.copy()
##                affi_linked = True
##            else:
##                i_aff = 1
##                options = {}
##                max_likelu = 0
##                map_id = 0
##                for affi_id in likely_affis:
##                    v_aff = str(affi_id) + "|"+ str(likely_affis[affi_id][0]) + str(likely_affis[affi_id][1]) + str(likely_affis[affi_id][2])
##                    options[i_aff] = v_aff
##                    i_aff += 1
##                    if likely_affis[affi_id][1] > 0.7 and likely_affis[affi_id][1] > max_likelu:
##                        map_id = affi_id
##                        max_likelu = likely_affis[affi_id][1]
##                if max_likelu != 0:
##                    print('Map to ID', map_id)
##                    if 'affiliations' in link_data:
##                        link_data.pop('affiliations')
##                    link_data['AffiliationID'] = map_id
##                    new_link_id = len(links_list)+1
##                    links_list[new_link_id] = link_data.copy()
##                    affi_linked = True
##                options[i_aff] = "split and add"
##                usr_select = "0"
##                while not affi_linked:
##                    for opt in options:
##                        print(opt, "Map to:", options[opt])
##                    print("Selection:")
##                    usr_select = int(input())
##                    keys = list(options.keys())
##                    if usr_select in keys:
##                        print("Selected:", options[usr_select])
##                        if usr_select == max(options):
##                            affi_records, new_id = add_affiliation(affi_text, affi_records)
##                            print('Adde ID', new_id)
##                            if 'affiliations' in link_data: 
##                                link_data.pop('affiliations')
##                            link_data['AffiliationID'] = new_id
##                            links_list[len(links_list)+1] = link_data.copy()
##                            affi_linked = True
##                        else:
##                            map_id = options[usr_select].split("|")[0]
##                            print('Map to ID', map_id)
##                            if 'affiliations' in link_data:
##                                link_data.pop('affiliations')
##                            link_data['AffiliationID'] = map_id
##                            new_link_id = len(links_list)+1
##                            links_list[new_link_id] = link_data.copy()
##                            affi_linked = True
##                    break
##                    
##    if counter == 400:
##        break
##
##with open(out_affi_file, 'w', newline='') as csvfile:
##    writer = csv.DictWriter(csvfile, fieldnames=affi_fields)
##    writer.writeheader()
##    for afi_num in affi_records.keys():
##        writer.writerow(affi_records[afi_num])
##        
##link_fields = new_affi_fields
##link_fields.remove("affiliations")
##link_fields.append("AffiliationID")
##link_fields.append("LinkID")
##
##with open(out_links_file, 'w', newline='') as csvfile:
##    writer = csv.DictWriter(csvfile, fieldnames=link_fields)
##    writer.writeheader()
##    for link_num in links_list.keys():
##        links_list[link_num]['LinkID'] = link_num
##        writer.writerow(links_list[link_num])
        
