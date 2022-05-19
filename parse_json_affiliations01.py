# Libraries
# library containign functions that read and write to csv files
import lib.handle_csv as csvh
# library for getting data from crossref
import lib.crossref_api as cr_api
# library for mapping json data
import lib.handle_json as hjson
# library for connecting to the db
import lib.handle_db as dbh

from datetime import datetime

def check_list(a_string, a_list):
    return_str = ""
    temp_str = ""
    for an_item in a_list:
        if an_item in a_string:
            if len(an_item) > len(temp_str):
                temp_str = an_item
    if len(temp_str)>0:
        a_string = a_string.replace(temp_str,"")
        return_str = temp_str
    return return_str, a_string

# Split the affiliation
# if affiliatin is found in DB:
#    retrieve affiliation ID and address ID
# else:
#    add affiliation and address to the DB
#    get the IDs of affiliation and address
# return affiliation ID and address ID
def db_split(affiliation):
    affiliation_id = 0
    address_id = 0
    fields={'a':'institution', 'b':'country', 'c':'department','d':'faculty',
            'e':'work_group','f':'address', 'g':'school'}
    print (affiliation, len(affiliation))
    for indx in range(0, len(affiliation)):
        inst_str = dept_str = faculty_str = group_str = ctry_str = school_str = ""
        qry_where_str = ""
        addr_list=[]
        
        checking_this = affiliation[indx]['name']
        #print (affiliation[indx]['name'])
        for inst in institution_synonyms.keys():
            if inst in checking_this:
                inst_str = institution_synonyms[inst]
                checking_this = checking_this.replace(inst,'')
                break
        # Institution 
        inst_str, checking_this = check_list(checking_this,institutions_list)

        # Country Synonyms
        for ctry in country_synonyms.keys():
            if ctry in checking_this:
                ctry_str = country_synonyms[ctry]
                checking_this = checking_this.replace(ctry,'')
                break
        
        for ctry in countries_list:
            if ctry in checking_this:
                ctry_str = inst
                checking_this = checking_this.replace(ctry,'')
                break
        
        # see if department in affiliation string
        dept_str, checking_this = check_list(checking_this, department_list)
            
        # find schools in affiliation string
        school_str, checking_this = check_list(checking_this, school_list)

                
        for fclty in faculty_list:
            if fclty in checking_this:
                faculty_str = fclty
                checking_this = checking_this.replace(dept,'')
                break
        for grp in group_list:
            if grp in checking_this:
                group_str = grp
                checking_this = checking_this.replace(grp,'')
                break
        checking_this = checking_this.strip()
        checking_this = checking_this.replace("  ", " ")
        addr_list.append(checking_this)
        
        result=-1
        print ('Institution:', inst_str)
        print ('School:', school_str)
        print ('Department:', dept_str)
        print ('Faculty:', faculty_str)
        print ('Group:', group_str)
        print ('Country:', ctry_str)

        print ('Address',  addr_list)
        if inst_str != "":
            affiliation_id, address_id = find_or_add(inst_str, dept_str, faculty_str, group_str, ctry_str, school_str, addr_list)
        else:        
            print("***************** get institution **************************************")
            print("split and add this: ", checking_this)
            addr_list.pop(0)
            ins_str = extract_custom(checking_this)
            checking_this = checking_this.replace(ins_str,'')
            checking_this = checking_this.strip()
            checking_this = checking_this.replace("  ", " ")
            addr_list.append(checking_this)
            affiliation_id, address_id = find_or_add(ins_str, dept_str, faculty_str, group_str, ctry_str, school_str, addr_list)
    return affiliation_id, address_id

def add_affi_to_db(inst_str, dept_str, faculty_str, group_str, ctry_str, school_str, addr_list, qry_where):
    ret_parsed = {}
    ret_parsed['institution'] = inst_str
    ret_parsed['school'] = school_str
    ret_parsed['department'] = dept_str
    ret_parsed['faculty'] = faculty_str
    ret_parsed['work_group'] = group_str
    ret_parsed['country'] = ctry_str
    ret_parsed['created_at'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    ret_parsed['updated_at'] = ret_parsed['created_at'] 
    print("** Will Add:", ret_parsed, " with address ", addr_list)
    db_conn.put_values_table("affiliations", ret_parsed.keys(), ret_parsed.values())
    result = db_conn.get_values("affiliations","id",qry_where)
    affi_id = result[0][0]
    print("Added:", result, len(result))
    addr_str = "; ".join(addr_list)
    affi_address = {'add_01':addr_str,"affiliation_id":affi_id,'country':ctry_str}
    db_conn.put_values_table("affiliation_addresses", affi_address.keys(), affi_address.values())
    add_id = db_conn.get_value("affiliation_addresses", "id", "affiliation_id", affi_id)[0]
    print('affiliation id:', affi_id, " address id: ", add_id)
    return affi_id, add_id


def find_or_add(inst_str, dept_str, faculty_str, group_str, ctry_str, school_str, addr_list):
    qry_where = ""
    if inst_str != "":
        qry_where += "institution = '" + inst_str + "'"
        if dept_str != "":
            qry_where += " AND department = '" + dept_str + "'"
        if faculty_str != "":
            qry_where += " AND faculty = '" + faculty_str + "'"
        if group_str != "":
            qry_where += " AND work_group = '" + group_str + "'"
        if school_str != "":
            qry_where += " AND school = '" + school_str + "'"
        if ctry_str != "":
            qry_where += " AND country = '" + ctry_str + "'"
        print(qry_where)
        result = db_conn.get_values("affiliations","id",qry_where)
        if result != []:
            affi_id = result[0][0]
            print("Found:", affi_id, len(result))
            add_id = db_conn.get_value("addresses", "id", "affiliation_id", affi_id)[0]
            print('affiliation id:', affi_id, " address id: ", add_id)
            return affi_id, add_id
        # not found, add new institution record
        else:
            affi_id, add_id = add_affi_to_db(inst_str, dept_str, faculty_str, group_str, ctry_str, school_str, addr_list, qry_where)
            return affi_id, add_id
    return 0, 0

def extract_custom(split_this):
    print( split_this)
    decimal_str = ""
    for indx in range(0, len(split_this)):
        val = " "
        if (indx % 10 == 0): val = str(int(indx/10)) 
        decimal_str += val
    print(decimal_str)
    unit_str = ""
    for indx in range(0, len(split_this)):
        val = str(indx%10)
        if (indx % 10 == 0): val = "0" 
        unit_str += val
    print(unit_str)
    print("start")
    str_start = int(input())
    print("end")
    str_end = int(input())
    return split_this[str_start:str_end+1]

def is_address(affi_element):
    while True:
        print ("************************SELECT OPTION*************************")
        print (affi_element,": \n a) address \n b) new affi \n c) str affi")
        print ("selection:", end=" ")
        user_select = input().lower()
        if user_select == 'a':
            return 1
        elif user_select == 'b':
            return 0
        elif user_select == 'c':
            return -1

def assing_keyword(affi_element):
    while True:
        print ("****************ASSIGN KEYWORD TO ELEMENT****************")
        print ("* Element:",affi_element)
        for opt in affi_keys:
            print (opt+")", affi_keys[opt])
        print ("x) None")
        print ("selection:", end=" ")
        user_select = input().lower()
        if user_select in affi_keys:
            return affi_keys[user_select]
        elif user_select == "x":
            return ""

def assign_not_mapped(list_affis, not_mapped):
    for element in not_mapped:
        print(element)
        print ("************************MAPPED AFFIS*************************")
        affi_keyword = assing_keyword(element)
        for i, affi in enumerate(list_affis):
            print (i, affi)
        while True:
            print ("******************ASSIGN NOT MAPPED TO AFFIS******************")
            print(element)
            print ("select number to assing to from above or 9 to assign to new affiliation")
            print ("selection:", end=" ")
            user_select = input()
            try:
                user_select = int(user_select)
                if user_select < len(list_affis):
                    if not affi_keyword in list_affis[user_select].keys():
                        list_affis[user_select][affi_keyword] = element
                        break;
                    else:
                        print ("cannot add")
                elif user_select == 9:
                    list_affis.append({affi_keyword:element})
                    break
            except:
                print("select a valid index")
        return list_affis
    
def get_keyword(affi_element):
    if affi_element in institutions_list:
        return "institution"
    elif affi_element in institution_synonyms:
        return "institution"
    elif affi_element in department_list:
        return "department"
    elif affi_element in faculty_list:
        return "faculty"
    elif affi_element in group_list: 
        return "work_group"
    elif affi_element in countries_list:
        return "country"
    elif affi_element in country_synonyms:
        return "country"
    else:
        return ""

# returns a list of dictionaries with affiliation values
def map_split_affi(affiliation):
    parsed_affi = { }
    affis_count = 0
    list_affis = []
    addr_list = []
    not_mapped = []
    for affi_element in affiliation:
        element_value = affi_element['name']
        element_key = get_keyword(element_value)
        if element_key == "":
            # Not found it could be a single string or an address element
            # ask if address or new affi
            is_addr = is_address(element_value)
            if is_addr == 1: # address part
                addr_list.append(element_value)
            elif is_addr == 0: # new affi part
                not_mapped.append(element_value)
            elif is_addr == -1: # new affi part
                print("not handled", element_value)
        else:
            if not element_key in parsed_affi:
                parsed_affi[element_key] = element_value
            else:
                # There is more than one affiliation
                parsed_affi['addr'] = addr_list
                list_affis.append(parsed_affi)
                parsed_affi = {}
                addr_list = []
                parsed_affi[element_key] = element_value
                affis_count += 1
        if affis_count > 0 and parsed_affi != {}:
            if addr_list != []:
                parsed_affi['addr'] = addr_list
            list_affis.append(parsed_affi)
    return list_affis, not_mapped

def get_afi_id(affiliation):
    print (affiliation, len(affiliation))
    inst_str = dept_str = faculty_str = group_str = ctry_str = ""
    qry_where_str = ""
    addr_list=[]
    for indx in range(0, len(affiliation)):
        checking_this = affiliation[indx]['name']
        #print (affiliation[indx]['name'])
        if checking_this in institutions_list:
            if inst_str == "":
                inst_str = checking_this
        elif checking_this in department_list:
            if inst_str == "":
                dept_str = checking_this
        elif checking_this in faculty_list:
            faculty_str = checking_this
        elif checking_this in group_list: 
            group_str = checking_this
        elif checking_this in countries_list:
            ctry_str = checking_this
        elif checking_this in country_synonyms:
            ctry_str = country_synonyms[checking_this]
        elif checking_this in institution_synonyms:
            inst_str = institution_synonyms[checking_this]
        else:
            addr_list.append(checking_this)
            
    qry_where_str += "institution = '" + inst_str + "'"        
    qry_where_str += " AND department = '" + dept_str + "'"
    qry_where_str += " AND faculty = '" + faculty_str + "'"
    qry_where_str += " AND work_group = '" + group_str + "'"
    qry_where_str += " AND country = '" + ctry_str + "'"

    print ('Institution:', inst_str)
    print ('Department:', dept_str)
    print ('Faculty:', faculty_str)
    print ('Group:', group_str)
    print ('Country:', ctry_str) 
    print ('Address',  addr_list)
    print (qry_where_str)
    result = db_conn.get_values("affiliations","id",qry_where_str)
    print("found",result)
    if result != []:
            affi_id = result[0][0]
            print("Found:", affi_id, len(result))
            add_id = db_conn.get_value("affiliation_addresses", "id", "affiliation_id", affi_id)[0]
            print('affiliation id:', affi_id, " address id: ", add_id)
            addr_row = list(db_conn.get_row("affiliation_addresses", add_id)[0])
            print(addr_row)
            another_affi=[]
            for indx in range(0, len(affiliation)):
                checking_this = affiliation[indx]['name']
                print(checking_this)
                if not checking_this in [inst_str, dept_str, faculty_str, group_str, ctry_str]:
                    if not(checking_this in country_synonyms.keys()):
                        skip = False
                        for add_itm in addr_row:
                            if str(add_itm) in checking_this:
                                skip = True
                                break;
                        if not skip:
                            another_affi.append({'name':checking_this})
                        
            if another_affi != []:
                get_afi_id(another_affi)
            return affi_id, add_id
    else:
        # add new affiliation
        affi_id, add_id = add_affi_to_db(inst_str, dept_str, faculty_str, group_str, ctry_str, addr_list,qry_where_str)
        return affi_id, add_id
          

#db_conn = dbh.DataBaseAdapter('db_files/production.sqlite3')
        

db_conn = dbh.DataBaseAdapter('./db_files/app_db202205.sqlite3')


# get institutions list from affiliations table
institutions_list = db_conn.get_value_list("affiliations", "institution")
# get coutries from affiliations table
countries_list = db_conn.get_value_list("affiliations","country")
# get school list from affiliations table
school_list = db_conn.get_value_list("Affiliations","school")
# get department list from affiliations table
department_list = db_conn.get_value_list("affiliations","department")
# get faculty list from affiliations table
faculty_list = db_conn.get_value_list("affiliations","faculty")
# get research group list from affiliations table
group_list = db_conn.get_value_list("affiliations", "work_group")

affi_keys = {'a':'institution', 'b':'country', 'c':'department','d':'faculty',
             'e':'work_group'}

country_synonyms = {'UK':'United Kingdom','U.K.':'United Kingdom',
                    'G.B.':'United Kingdom', "USA":"United States",
                    "U.S.A.":"United States", "China":"P. R. China",
                    "P.R.C.":"P. R. China"}

institution_synonyms = {"Paul Scherrer Institut":"Paul Scherrer Institute",
                        "PSI":"Paul Scherrer Institute",
                        "Diamond Light Source": "Diamond Light Source Ltd.",
                        "Diamond Light source Ltd": "Diamond Light Source Ltd.",
                        "University of St Andrews": "University of St. Andrews"}  
##

##
##affis = [[{'name': 'Department of ChemistryUniversity of Cambridge Cambridge CB2 1EW UK'}],[{'name': 'Department of ChemistryUniversity of Cambridge Cambridge CB2 1EW UK'}],[{'name': 'Department of ChemistryUniversity of Reading Reading RG6 6AD UK'}],
##         [{'name': 'Department of ChemistryUniversity of Reading Reading RG6 6AD UK'}],[{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],
##         [{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],[{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],
##         [{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],[{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],
##         [{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],[{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],
##         [{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],[{'name': 'ISIS FacilityRutherford Appleton Laboratory Chilton Didcot OX11 0QX UK'}],
##         [{'name': 'ISIS FacilityRutherford Appleton Laboratory Chilton Didcot OX11 0QX UK'}],[{'name': 'Johnson Matthey Technology Centre Reading RG4 9NH UK'}],[{'name': 'Johnson Matthey Technology Centre Reading RG4 9NH UK'}],
##         [{'name': 'School of ChemistryUniversity of St Andrews North Haugh St Andrews KY16 9ST UK'}],[{'name': 'School of ChemistryUniversity of St Andrews North Haugh St Andrews KY16 9ST UK'}],
##         [{'name': 'School of Science Engineering and EnvironmentUniversity of Salford Manchester M5 4WT UK'}],[{'name': 'School of Science Engineering and EnvironmentUniversity of Salford Manchester M5 4WT UK'}],
##         [{'name': 'Department of ChemistryUniversity College London London WC1H 0AJ UK'}, {'name': 'UK Catalysis Hub Research Complex at Harwell (RCaH)Rutherford Appleton Laboratory Harwell Oxon OX11 0FA UK'}],
##         [{'name': 'Department of ChemistryUniversity College London London WC1H 0AJ UK'}, {'name': 'UK Catalysis Hub Research Complex at Harwell (RCaH)Rutherford Appleton Laboratory Harwell Oxon OX11 0FA UK'}],
##         [{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}, {'name': 'Department of ChemistryUniversity of Reading Reading RG6 6AD UK'}],
##         [{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}, {'name': 'Department of ChemistryUniversity of Reading Reading RG6 6AD UK'}],
##         [{'name': 'Diamond Light Source Ltd.'}, {'name': 'Didcot'}, {'name': 'UK'}],[{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],
##         [{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],[{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],
##         [{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],[{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],
##         [{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],[{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],
##         [{'name': 'Paul Scherrer Institut'}, {'name': '5232 Villigen'}, {'name': 'Switzerland'}],[{'name': 'Paul Scherrer Institut'}, {'name': '5232 Villigen'}, {'name': 'Switzerland'}],
##         [{'name': 'Paul Scherrer Institut'}, {'name': '5232 Villigen'}, {'name': 'Switzerland'}],[{'name': 'Paul Scherrer Institut'}, {'name': '5232 Villigen'}, {'name': 'Switzerland'}],
##         [{'name': 'Department of Chemical and Biomolecular Engineering'}, {'name': 'Yonsei University'}, {'name': 'Seoul 03722'}, {'name': 'South Korea'}],
##         [{'name': 'Department of Chemical and Biomolecular Engineering'}, {'name': 'Yonsei University'}, {'name': 'Seoul 03722'}, {'name': 'South Korea'}],
##         [{'name': 'Department of Chemical and Biomolecular Engineering'}, {'name': 'Yonsei University'}, {'name': 'Seoul 03722'}, {'name': 'South Korea'}],
##         [{'name': 'Department of Chemical and Biomolecular Engineering'}, {'name': 'Yonsei University'}, {'name': 'Seoul 03722'}, {'name': 'South Korea'}],
##         [{'name': 'School of Chemistry'}, {'name': 'University of Bristol'}, {'name': 'Bristol'}, {'name': 'UK'}],[{'name': 'School of Chemistry'}, {'name': 'University of Bristol'}, {'name': 'Bristol'}, {'name': 'UK'}],
##         [{'name': 'Department of Chemical Engineering'}, {'name': 'University of Bath'}, {'name': 'Bath'}, {'name': 'UK'}, {'name': 'Department of Chemical Engineering'}],
##         [{'name': 'Department of Chemical Engineering'}, {'name': 'University of Bath'}, {'name': 'Bath'}, {'name': 'UK'}, {'name': 'Department of Chemical Engineering'}],
##         [{'name': 'Department of Chemical Engineering'}, {'name': 'University of Bath'}, {'name': 'Bath'}, {'name': 'UK'}, {'name': 'Department of Chemical Engineering'}],
##         [{'name': 'Department of Chemical Engineering'}, {'name': 'University of Bath'}, {'name': 'Bath'}, {'name': 'UK'}, {'name': 'Department of Chemical Engineering'}],
##         [{'name': 'Department of Chemical Engineering'}, {'name': 'University of Bath'}, {'name': 'Bath'}, {'name': 'UK'}, {'name': 'School of Chemistry'}],
##         [{'name': 'Department of Chemical Engineering'}, {'name': 'University of Bath'}, {'name': 'Bath'}, {'name': 'UK'}, {'name': 'School of Chemistry'}],
##         [{'name': 'Department of Chemistry'}, {'name': 'University College London'}, {'name': 'London'}, {'name': 'UK'}, {'name': 'UK Catalysis Hub'}],
##         [{'name': 'Department of Chemistry'}, {'name': 'University College London'}, {'name': 'London'}, {'name': 'UK'}, {'name': 'UK Catalysis Hub'}],
##         [{'name': 'Department of Chemistry'}, {'name': 'University College London'}, {'name': 'London'}, {'name': 'UK'}, {'name': 'UK Catalysis Hub'}],
##         [{'name': 'Department of Chemistry'}, {'name': 'University College London'}, {'name': 'London'}, {'name': 'UK'}, {'name': 'UK Catalysis Hub'}],
##         [{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}, {'name': 'Electron Physical Sciences Imaging Centre (ePSIC)'}, {'name': 'Diamond Light source Ltd'}],
##         [{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratories'}, {'name': 'Harwell Science & Innovation Campus'}, {'name': 'Didcot'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratories'}, {'name': 'Harwell Science & Innovation Campus'}, {'name': 'Didcot'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratory'}, {'name': 'Didcot OX11 0FA'}, {'name': 'UK'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratory'}, {'name': 'Didcot OX11 0FA'}, {'name': 'UK'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratory'}, {'name': 'Didcot OX11 0FA'}, {'name': 'UK'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratory'}, {'name': 'Didcot OX11 0FA'}, {'name': 'UK'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratory'}, {'name': 'Didcot OX11 0FA'}, {'name': 'UK'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratory'}, {'name': 'Didcot OX11 0FA'}, {'name': 'UK'}]]
##
##affis = [[{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}, {'name': 'Electron Physical Sciences Imaging Centre (ePSIC)'}, {'name': 'Diamond Light source Ltd'}],[{'name': 'Department of Chemistry'}, {'name': 'University College London'}, {'name': 'London'}, {'name': 'UK'}, {'name': 'UK Catalysis Hub'}]]
##
# get list of non parsed article author ids

aut_affi_ids = db_conn.get_values('cr_affiliations', 'article_author_id', 'author_affiliation_id is NULL')
flat_list = []
for sublist in aut_affi_ids:
    for item in sublist:
        flat_list.append(item)

i_idx = 0
aut_affi_ids = list(set(flat_list))
for aai in aut_affi_ids:
    print("Art. author", aai)
    non_parsed_affis = db_conn.get_values('cr_affiliations', 'name', 'article_author_id = '+ str(aai))
    json_affis = []
    for sublist in non_parsed_affis:
        for item in sublist:
            json_affis.append({'name':item})

    print("PARSING", json_affis)
    list_affis, not_mapped = map_split_affi(json_affis)
    if not_mapped != []:
        print('****** There are some not mapped affis ******')
        print('* Not mapped: ', not_mapped)
        list_affis = assign_not_mapped(list_affis, not_mapped)
    print('* List mapped affis:', list_affis)
    print('*********************************************')
##    #print(map_split_affi(affi))
    if len(json_affis) == 1:
        affiliation_id, address_id = db_split(json_affis)
        print("Returned IDs:", affiliation_id, address_id, "for art. author", aai)
        # got some IDs so map to add article_author
    elif len(json_affis) == 2:
        affiliation_id, address_id = db_split(json_affis)
        print("Returned IDs:", affiliation_id, address_id, "for art. author", aai)
    elif len(json_affis) > 2:
        get_afi_id(json_affis)
    if i_idx == 0:
        break
    i_idx+=1
