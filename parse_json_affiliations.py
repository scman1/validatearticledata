
# Libraries
# library containign functions that read and write to csv files
import lib.handle_csv as csvh
# library for getting data from crossref
import lib.crossref_api as cr_api
# library for mapping json data
import lib.handle_json as hjson
# library for connecting to the db
import lib.handle_db as dbh


def add_affiliation(affiliation):
    affiliation, address = split_and_assign(affiliation)
    new_id = len(affi_records) + 1
    affi_records[new_id] = affiliation
    affi_records[new_id]["ID"] = new_id
    return affi_records, new_id

def db_split(affiliation):
    fields={'a':'institution', 'b':'country', 'c':'department','d':'faculty',
            'e':'work_group','f':'address'}
    print (affiliation, len(affiliation))
    for indx in range(0, len(affiliation)):
        inst_str = dept_str = faculty_str = group_str = ctry_str = ""
        qry_where_str = ""
        addr_list=[]
        
        checking_this = affiliation[indx]['name']
        #print (affiliation[indx]['name'])
        for inst in institution_synonyms.keys():
            if inst in checking_this:
                inst_str = institution_synonyms[inst]
                checking_this = checking_this.replace(inst,'')
                break
        for inst in institutions_list:
            if inst in checking_this:
                if inst_str == "":
                    inst_str = inst
                    checking_this = checking_this.replace(inst,'')
                elif len(inst) > len(inst_str):
                    rep_str = inst.replace(inst_str, "")
                    inst_str = inst
                    checking_this = checking_this.replace(rep_str,'')
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
        for dept in department_list:
            if dept in checking_this:
                dept_str = dept
                checking_this = checking_this.replace(dept,'')
                break
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
        print ('Department:', dept_str)
        print ('Faculty:', faculty_str)
        print ('Group:', group_str)
        print ('Country:', ctry_str) 
        print ('Address',  addr_list)
        if inst_str != "":
            find_or_add(inst_str, dept_str, faculty_str, group_str, ctry_str, addr_list)
        else:
            print("***************** get institution **************************************")
            print("split and add this: ", checking_this)
            addr_list.pop(0)
            ins_str = extract_custom(checking_this)
            checking_this = checking_this.replace(ins_str,'')
            
            checking_this = checking_this.strip()
            checking_this = checking_this.replace("  ", " ")
            addr_list.append(checking_this)
            
            find_or_add(ins_str, dept_str, faculty_str, group_str, ctry_str, addr_list)
            
def find_or_add(inst_str, dept_str, faculty_str, group_str, ctry_str, addr_list):
    ret_parsed = {}
    qry_where = ""
    if inst_str != "":
        qry_where += "institution = '" + inst_str + "'"
        if dept_str != "":
            qry_where += " AND department = '" + dept_str + "'"
        if faculty_str != "":
            qry_where += " AND faculty = '" + faculty_str + "'"
        if group_str != "":
            qry_where += " AND group = '" + group_str + "'"
        if ctry_str != "":
            qry_where += " AND country = '" + ctry_str + "'"
        print(qry_where)
        result = db_conn.get_values("affiliations","id",qry_where)
        if result != []:
            affi_id = result[0][0]
            print("Found:", affi_id, len(result))
            add_id = db_conn.get_value("affiliation_addresses", "id", "affiliation_id", affi_id)[0]
            print('affiliation id:', affi_id, " address id: ", add_id)
            return affi_id, add_id
        # not found, add new institution record
        else:
            ret_parsed['institution'] = inst_str
            ret_parsed['department'] = dept_str
            ret_parsed['faculty'] = faculty_str
            ret_parsed['work_group'] = group_str
            ret_parsed['country'] = ctry_str
            print("** Will Add:", ret_parsed, " with address ", addr_list)
            db_conn.put_values_table("affiliations", ret_parsed.keys(), ret_parsed.values())
            result = db_conn.get_values("affiliations","id",qry_where)
            affi_id = result[0][0]
            print("Added:", result, len(result))
            affi_address = {'add_01':addr_list[0],"affiliation_id":affi_id,'country':ctry_str}
            db_conn.put_values_table("affiliation_addresses", affi_address.keys(), affi_address.values())
            add_id = db_conn.get_value("affiliation_addresses", "id", "affiliation_id", affi_id)[0]
            print('affiliation id:', affi_id, " address id: ", add_id)
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

def get_afi_id(affiliation):
    print (affiliation, len(affiliation))
    inst_str = dept_str = faculty_str = group_str = ctry_str = ""
    qry_where_str = ""
    addr_list=[]
    for indx in range(0, len(affiliation)):
        checking_this = affiliation[indx]['name']
        #print (affiliation[indx]['name'])
        if checking_this in institutions_list:
            inst_str = checking_this
        elif checking_this in department_list:
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
    if dept_str != "":
        qry_where_str += " AND department = '" + dept_str + "'"
    if faculty_str != "":
        qry_where_str += " AND faculty = '" + faculty_str + "'"
    if group_str != "":
        qry_where_str += " AND group = '" + group_str + "'"
    if ctry_str != "":
        qry_where_str += " AND country = '" + ctry_str + "'"
    print ('Institution:', inst_str)
    print ('Department:', dept_str)
    print ('Faculty:', faculty_str)
    print ('Group:', group_str)
    print ('Country:', ctry_str) 
    print ('Address',  addr_list)
    print (qry_where_str)
    result = db_conn.get_values("affiliations","id",qry_where_str)
    if len(result) == 1 :
        return result[0][0]
    else:
        # add new affiliation
        result = db_split(affiliation)
        

db_conn = dbh.DataBaseAdapter('ukch_articles.sqlite')

# get institutions list from affiliations table
institutions_list = db_conn.get_value_list("Affiliations", "institution")
# get coutries from affiliations table
countries_list = db_conn.get_value_list("Affiliations","country")
# get department list from affiliations table
department_list = db_conn.get_value_list("Affiliations","department")
# get faculty list from affiliations table
faculty_list = db_conn.get_value_list("Affiliations","faculty")
# get research group list from affiliations table
group_list = db_conn.get_value_list("Affiliations", "work_group")


country_synonyms = {'UK':'United Kingdom','U.K.':'United Kingdom',
                    'G.B.':'United Kingdom', "USA":"United States",
                    "U.S.A.":"United States", "China":"P. R. China",
                    "P.R.C.":"P. R. China"}

institution_synonyms = {"Paul Scherrer Institut":"Paul Scherrer Institute",
                        "PSI":"Paul Scherrer Institute",
                        "Diamond Light Source": "Diamond Light Source Ltd.",
                        "University of St Andrews": "University of St. Andrews"}

affis = [[{'name': 'Department of ChemistryUniversity of Cambridge Cambridge CB2 1EW UK'}],[{'name': 'Department of ChemistryUniversity of Cambridge Cambridge CB2 1EW UK'}],[{'name': 'Department of ChemistryUniversity of Reading Reading RG6 6AD UK'}],
         [{'name': 'Department of ChemistryUniversity of Reading Reading RG6 6AD UK'}],[{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],
         [{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],[{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],
         [{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],[{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],
         [{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],[{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],
         [{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}],[{'name': 'ISIS FacilityRutherford Appleton Laboratory Chilton Didcot OX11 0QX UK'}],
         [{'name': 'ISIS FacilityRutherford Appleton Laboratory Chilton Didcot OX11 0QX UK'}],[{'name': 'Johnson Matthey Technology Centre Reading RG4 9NH UK'}],[{'name': 'Johnson Matthey Technology Centre Reading RG4 9NH UK'}],
         [{'name': 'School of ChemistryUniversity of St Andrews North Haugh St Andrews KY16 9ST UK'}],[{'name': 'School of ChemistryUniversity of St Andrews North Haugh St Andrews KY16 9ST UK'}],
         [{'name': 'School of Science Engineering and EnvironmentUniversity of Salford Manchester M5 4WT UK'}],[{'name': 'School of Science Engineering and EnvironmentUniversity of Salford Manchester M5 4WT UK'}],
         [{'name': 'Department of ChemistryUniversity College London London WC1H 0AJ UK'}, {'name': 'UK Catalysis Hub Research Complex at Harwell (RCaH)Rutherford Appleton Laboratory Harwell Oxon OX11 0FA UK'}],
         [{'name': 'Department of ChemistryUniversity College London London WC1H 0AJ UK'}, {'name': 'UK Catalysis Hub Research Complex at Harwell (RCaH)Rutherford Appleton Laboratory Harwell Oxon OX11 0FA UK'}],
         [{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}, {'name': 'Department of ChemistryUniversity of Reading Reading RG6 6AD UK'}],
         [{'name': 'Diamond Light SourceHarwell Science and Innovation Campus Didcot OX11 0DE UK'}, {'name': 'Department of ChemistryUniversity of Reading Reading RG6 6AD UK'}],
         [{'name': 'Diamond Light Source Ltd.'}, {'name': 'Didcot'}, {'name': 'UK'}],[{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],
         [{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],[{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],
         [{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],[{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],
         [{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],[{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}],
         [{'name': 'Paul Scherrer Institut'}, {'name': '5232 Villigen'}, {'name': 'Switzerland'}],[{'name': 'Paul Scherrer Institut'}, {'name': '5232 Villigen'}, {'name': 'Switzerland'}],
         [{'name': 'Paul Scherrer Institut'}, {'name': '5232 Villigen'}, {'name': 'Switzerland'}],[{'name': 'Paul Scherrer Institut'}, {'name': '5232 Villigen'}, {'name': 'Switzerland'}],
         [{'name': 'Department of Chemical and Biomolecular Engineering'}, {'name': 'Yonsei University'}, {'name': 'Seoul 03722'}, {'name': 'South Korea'}],
         [{'name': 'Department of Chemical and Biomolecular Engineering'}, {'name': 'Yonsei University'}, {'name': 'Seoul 03722'}, {'name': 'South Korea'}],
         [{'name': 'Department of Chemical and Biomolecular Engineering'}, {'name': 'Yonsei University'}, {'name': 'Seoul 03722'}, {'name': 'South Korea'}],
         [{'name': 'Department of Chemical and Biomolecular Engineering'}, {'name': 'Yonsei University'}, {'name': 'Seoul 03722'}, {'name': 'South Korea'}],
         [{'name': 'School of Chemistry'}, {'name': 'University of Bristol'}, {'name': 'Bristol'}, {'name': 'UK'}],[{'name': 'School of Chemistry'}, {'name': 'University of Bristol'}, {'name': 'Bristol'}, {'name': 'UK'}],
         [{'name': 'Department of Chemical Engineering'}, {'name': 'University of Bath'}, {'name': 'Bath'}, {'name': 'UK'}, {'name': 'Department of Chemical Engineering'}],[{'name': 'Department of Chemical Engineering'}, {'name': 'University of Bath'}, {'name': 'Bath'}, {'name': 'UK'}, {'name': 'Department of Chemical Engineering'}],[{'name': 'Department of Chemical Engineering'}, {'name': 'University of Bath'}, {'name': 'Bath'}, {'name': 'UK'}, {'name': 'Department of Chemical Engineering'}],[{'name': 'Department of Chemical Engineering'}, {'name': 'University of Bath'}, {'name': 'Bath'}, {'name': 'UK'}, {'name': 'Department of Chemical Engineering'}],[{'name': 'Department of Chemical Engineering'}, {'name': 'University of Bath'}, {'name': 'Bath'}, {'name': 'UK'}, {'name': 'School of Chemistry'}],[{'name': 'Department of Chemical Engineering'}, {'name': 'University of Bath'}, {'name': 'Bath'}, {'name': 'UK'}, {'name': 'School of Chemistry'}],[{'name': 'Department of Chemistry'}, {'name': 'University College London'}, {'name': 'London'}, {'name': 'UK'}, {'name': 'UK Catalysis Hub'}],[{'name': 'Department of Chemistry'}, {'name': 'University College London'}, {'name': 'London'}, {'name': 'UK'}, {'name': 'UK Catalysis Hub'}],[{'name': 'Department of Chemistry'}, {'name': 'University College London'}, {'name': 'London'}, {'name': 'UK'}, {'name': 'UK Catalysis Hub'}],[{'name': 'Department of Chemistry'}, {'name': 'University College London'}, {'name': 'London'}, {'name': 'UK'}, {'name': 'UK Catalysis Hub'}],[{'name': 'Johnson Matthey Technology Centre'}, {'name': 'Reading RG4 9NH'}, {'name': 'UK'}, {'name': 'Electron Physical Sciences Imaging Centre (ePSIC)'}, {'name': 'Diamond Light source Ltd'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratories'}, {'name': 'Harwell Science & Innovation Campus'}, {'name': 'Didcot'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratories'}, {'name': 'Harwell Science & Innovation Campus'}, {'name': 'Didcot'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratory'}, {'name': 'Didcot OX11 0FA'}, {'name': 'UK'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratory'}, {'name': 'Didcot OX11 0FA'}, {'name': 'UK'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratory'}, {'name': 'Didcot OX11 0FA'}, {'name': 'UK'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratory'}, {'name': 'Didcot OX11 0FA'}, {'name': 'UK'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratory'}, {'name': 'Didcot OX11 0FA'}, {'name': 'UK'}],[{'name': 'UK Catalysis Hub'}, {'name': 'Research Complex at Harwell'}, {'name': 'Rutherford Appleton Laboratory'}, {'name': 'Didcot OX11 0FA'}, {'name': 'UK'}]]
#affis = [[{'name': 'Department of ChemistryUniversity of Reading Reading RG6 6AD UK'}]]

for affi in affis:
    if len(affi) == 1:
        db_split(affi)
    if len(affi) == 2:
        print(affi)
        db_split(affi)


