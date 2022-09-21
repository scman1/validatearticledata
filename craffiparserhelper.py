# library for connecting to the db
import lib.handle_db as dbh

# datetime parsing
from datetime import datetime

import craffiparser


def get_parser(db_):
    cr_parse = craffiparser.crp(db_)
    cr_parse.start_lists()
    return cr_parse

def refresh_lists(cr_parse):
    cr_parse.start_lists()

def get_all_affiliations(db_conn):
    a_table = 'affiliations'
    all_affiliations = db_conn.get_full_table(a_table)
    table_info = db_conn.get_table_info(a_table)
    affiliations_dict = []
    for an_affi in all_affiliations:
        a_dict_affi = {}
        for col_idx, col_val in enumerate(an_affi):
            a_dict_affi[table_info[col_idx][1]] = col_val
        affiliations_dict.append(a_dict_affi)
    return affiliations_dict

def get_cr_affis_article_author_ids(db_conn):
    a_table = 'cr_affiliations'
    a_column = 'article_author_id'
    cr_affis_article_author_ids = db_conn.get_value_list(a_table, a_column)
    return cr_affis_article_author_ids

def get_cr_lines_for_article_author_ids(db_conn, art_author_id):
    s_table = 'cr_affiliations'
    s_fields = '*'
    s_where = "article_author_id = %s"%(art_author_id)
    authors_list = db_conn.get_values(s_table, s_fields, s_where)
    return authors_list

def get_affiliation_id(db_conn, parsed_affi):
    s_table = 'affiliations'
    s_field = 'id'
    for k,v in parsed_affi.items():
        if "'" in v :parsed_affi[k]=v.replace("'","''")
    list_where = [ k +" = '"+ v +"'" for k,v in parsed_affi.items() if k != 'address']
    s_where = " AND ".join(list_where) 
    s_where = s_where.replace("= ''", "IS NULL")
    #print('Get affiliation id', s_where)
    affi_list = db_conn.get_values(s_table, s_field, s_where)
    affi_id = None
    if affi_list !=[]:
        affi_id = affi_list[0][0]
    return affi_id

# could correct the close affiliation to get all the ones with 
# same institution and compare closest match
def get_close_affiliation_id(db_conn, parsed_affi):
    affi_id = None
    if (len(parsed_affi) == 2 and 'country' in parsed_affi.keys()) or (len(parsed_affi) == 1 and not 'institution' in parsed_affi.keys()):
        print ("Not enough data to get close affi")
    else:
        print(parsed_affi)
        s_table = 'affiliations'
        s_field = 'id'
        for k,v in parsed_affi.items():
            if "'" in v :parsed_affi[k]=v.replace("'","''")
        list_where = [ k +" = '"+ v +"'" for k,v in parsed_affi.items() if k != 'address']
        s_where = " AND ".join(list_where) 
        s_where = s_where.replace("= ''", "IS NULL")
        #print('Get Close affiliation id:', s_where)
        affi_list = db_conn.get_values(s_table, s_field, s_where)
        if affi_list !=[]:
            affi_id = affi_list[0][0]
    return affi_id

#get the id of affiliation assigned to an author affiliation record
def get_auth_affi_affiliation_id(db_conn, aut_affi_id):
    s_table = 'author_affiliations'
    s_field = 'affiliation_id'
    s_where = " id = %i" %(aut_affi_id)
    #print (s_where)
    affi_list = db_conn.get_values(s_table, s_field, s_where)
    if affi_list !=[]:
        affi_list = list(set([an_id[0] for an_id in affi_list]))
    return affi_list

#get the ids the author affiliation records for a given author
def get_auth_affi_id_for_author(db_conn, art_aut_id):
    s_table = 'author_affiliations'
    s_field = 'id'
    s_where = " article_author_id = %i" %(art_aut_id)
    #print (s_where)
    affi_list = db_conn.get_values(s_table, s_field, s_where)
    if affi_list !=[]:
        affi_list = list(set([an_id[0] for an_id in affi_list]))
    return affi_list

#get the ids the author affiliation records for a given author
def get_value_from_affi(db_conn, column, affi_id):
    s_table = 'affiliations'
    s_field = 'country'
    s_where = " id = %i" %(affi_id)
    #print (s_where)
    affi_list = db_conn.get_values(s_table, s_field, s_where)
    affi_val = None
    if affi_list !=[]:
        affi_val = affi_list[0][0]
    return affi_val

def is_one_line_affi(cr_parser, str_affi):
    is_one_liner = False
    parsed_affi = cr_parser.split_single(str_affi)
    parsed_no_blanks = {k:v for k,v in parsed_affi.items() if v != ''}
    if len(parsed_no_blanks) > 1:
        is_one_liner = True
    return is_one_liner

def check_assigned_affi_ol(db_name, cr_parser, cr_affi):
    assigned_ok = False
    if cr_affi[3] != None:
        parsed_affi = cr_parser.split_single(cr_affi[1])
        parsed_no_blanks = {k:v for k,v in parsed_affi.items() if v != ''} 
        affi_id = get_affiliation_id(db_name, parsed_affi)
        if affi_id == None:
            affi_id = get_close_affiliation_id(db_name, parsed_no_blanks)
        assigned_affi_id = get_auth_affi_affiliation_id(db_name, cr_affi[3])[0]
        print('Assigned ID:', assigned_affi_id, "Recoverd ID:", affi_id)
        if assigned_affi_id == affi_id:
            assigned_ok = True
    return assigned_ok

def check_assigned_affi_ml(db_name, cr_parser, cr_affi_lines, art_aut_id):
    assigned_ok = True
    just_affi_lines = [x[1] for x in cr_affi_lines]
    parsed_affis = cr_parser.parse_multiline(just_affi_lines)
    # all affiliations belong to same article author
    aut_affis = get_auth_affi_id_for_author(db_name, art_aut_id)
    assigned_affis = []
    for an_aut_affi_id in aut_affis:
        assigned_affis.append(get_auth_affi_affiliation_id(db_name, an_aut_affi_id)[0])
 
    for one_parsed in parsed_affis:
        affi_id = get_affiliation_id(db_name, one_parsed)
        if affi_id == None:
            parsed_no_blanks = {k:v for k,v in one_parsed.items() if v != ''}
            affi_id = get_close_affiliation_id(db_name, parsed_no_blanks)
        if not affi_id in assigned_affis:
            print('Assigned ID:', affi_id, "not in recoverd IDs list:", assigned_affis)
            assigned_ok = False
        else:
            print('Assigned ID:', affi_id, "in recoverd IDs list:", assigned_affis)
    return assigned_ok

##############################################################################
# FIX AFFILIATION ISSUES
# Likely problems:
#   a) only one assigned to two affiliations
#      Fixes:
#        - add missing author affiliation
#        - correct exiting author affiliation 
#   b) Mismatch in assigned affiliation
#      Fixes:
#        - correct exiting author affiliation 
#   c) Affiliation not assigned
#      Fixes:
#        - try to assign from existing
#        - if no existing one, ask if new should be added

def get_affi_from_parsed(db_name, parsed_dict):
    affi_id = get_affiliation_id(db_name, parsed_dict)
    if affi_id == None:
        parsed_no_blanks = {k:v for k,v in parsed_dict.items() if v != ''}
        affi_id = get_close_affiliation_id(db_name, parsed_no_blanks)
    return affi_id


# all parsed lines should be assigned else cannot be assigned
def can_be_assigned(db_name, cr_parser, parsed_lines):
    #if any of the resulting parsed affis cannot be assigned then none can be
    can_assign = True
    for one_parsed in parsed_lines:
        affi_id = get_affi_from_parsed(db_name, one_parsed[0])
        if(affi_id == None):
            can_assign = False
    return can_assign

def correct_oneline(db_name, cr_parser, cr_affis):
    # get a list of parsed affis with the ids of the corresponding cr_records
    parsed_affis  =[]
    for a_cr_affi in cr_affis:
        parsed_affis += cr_parser.parse_and_map_single(a_cr_affi)
    print(parsed_affis)
    # all belong to same article author
    art_author_id = cr_affis[0][2]
    
    print ("verifying affiliations for article author", art_author_id)
    
    art_auth_affis = get_auth_affi_id_for_author(db_name, art_author_id)
    
    print ("Article author affiliations:", len(art_auth_affis), art_auth_affis )
    
    print ("Parsed article author affiliations:", len(parsed_affis) )

    for affi_idx, parsed_affi in enumerate(parsed_affis):
        print('processing', parsed_affi)
        affi_vals = parsed_affi[0]
        cr_affi_ids = parsed_affi[1]
        correct_this = 0
        if affi_idx < len(art_auth_affis):
            correct_this = art_auth_affis[affi_idx]#
        affi_id = get_affiliation_id(db_name, affi_vals)
        if affi_id == None:
            parsed_no_blanks = {k:v for k,v in affi_vals.items() if v != ''}
            affi_id = get_close_affiliation_id(db_name, parsed_no_blanks)
            if affi_id != None:
                affi_vals['country'] = get_value_from_affi(db_name, 'country', affi_id)
            ##############################################################################
            # if there is no close affiliation should ask if add, assign or ignore
            # in the case of orphan lines it is ignore

        if correct_this != 0:
            # the affiliation does not exist but something was assigned to author affi
            if affi_id == None:
                print('{0:*^80}'.format('Affi does not exist'))
                print(affi_vals)
                #affi_id = add_new_affiliation(db_name, affi_vals)
            # if the affiliation exists    
            if affi_id != None:
                print('{0:*^80}'.format('Update Author Affiliatio'))
                print('Update ID:', correct_this, 'with values:', affi_vals )
                update_author_affiliation(db_name, correct_this, affi_id, affi_vals)
                update_cr_aai(db_name, cr_affi_ids[0], correct_this)                
        else:
            if affi_id != None :
                print("Add author affiliation for author: ", art_author_id, 'with affi:', affi_vals) 
                new_affi_id = add_author_affiliation(db_name, art_author_id, affi_id, affi_vals)
                #update cr_affis (assign author_affi_id)
                print("Created ", new_affi_id, "for", cr_affi_ids)
                for cr_id in cr_affi_ids:
                    update_cr_aai(db_name, cr_id, new_affi_id)

def correct_multiline(db_name, cr_parser, cr_affis):
    # get a list of parsed affis with the ids of the corresponding cr_records
    parsed_affis = cr_parser.parse_and_map_multiline(cr_affis)
    print(parsed_affis)
    # all belong to same article author
    art_author_id = cr_affis[0][2]
    
    print ("verifying affiliations for article author", art_author_id)
    
    art_auth_affis = get_auth_affi_id_for_author(db_name, art_author_id)
    
    print ("Article author affiliations:", len(art_auth_affis), art_auth_affis )
    
    print ("Parsed article author affiliations:", len(parsed_affis) )
    
    if len(parsed_affis) > len(art_auth_affis):
        missing_author_affi = True

    for affi_idx, parsed_affi in enumerate(parsed_affis):
        affi_vals = parsed_affi[0]
        cr_affi_ids = parsed_affi[1]
        correct_this = 0
        if affi_idx < len(art_auth_affis):
            correct_this = art_auth_affis[affi_idx]

        affi_id = get_affiliation_id(db_name, affi_vals)
        if affi_id == None:
            parsed_no_blanks = {k:v for k,v in affi_vals.items() if v != ''}
            affi_id = get_close_affiliation_id(db_name, parsed_no_blanks)
            if affi_id != None:
                affi_vals['country'] = get_value_from_affi(db_name, ['country'], affi_id)
            ##############################################################################
            # if there is no close affiliation should ask if add, assign or ignore
            # in the case of orphan lines it is ignore
            
        if correct_this != 0:
            # if the affiliation exists
            if affi_id != None:
                print('Update author_affiliation:', correct_this, 'with affi:', affi_vals )
                update_author_affiliation(db_name, correct_this, affi_id, affi_vals)
                for cr_id in cr_affi_ids:
                    update_cr_aai(db_name, cr_id, correct_this)
                    #print("updating", cr_id, 'with', correct_this)
                    #input()
            else:
                print('Affi does not exist')
                print(affi_vals)
                
        else:
            if affi_id != None:
                print("Add author affiliation for author: ", art_author_id, 'with affi:', affi_vals) 
                new_affi_id = add_author_affiliation(db_name, art_author_id, affi_id, affi_vals)
                #update cr_affis (assign author_affi_id)
                print("Created ", new_affi_id, "for", cr_affi_ids)
                for cr_id in cr_affi_ids:
                    update_cr_aai(db_name, cr_id, new_affi_id)
                
def make_author_affiliation(art_aut_id, affi_values, addr_values):
    # get smallest unit
    smallest_unit = "" 
    #id Institution> Faculty > School > Department > Work_group + address + Country
    if affi_values[4] != None and  len(affi_values[4]) > 0: #'work_group'
        smallest_unit = affi_values[4]
    elif affi_values[2] != None and len(affi_values[2]) > 0 and smallest_unit == "": #'department'
        smallest_unit = affi_values[2]
    elif affi_values[9] != None and  len(affi_values[9]) > 0 and smallest_unit == "": #'school'
        smallest_unit = affi_values[9]
    elif affi_values[3] != None and len(affi_values[3]) > 0 and smallest_unit == "": #'faculty'
        smallest_unit = affi_values[3]
       
    ret_art_auth_affi = {}
    ret_art_auth_affi['article_author_id'] = art_aut_id
    if len(smallest_unit) > 0:
        ret_art_auth_affi['name'] = smallest_unit + ", "+  affi_values[1] #'institution'
    else:
        ret_art_auth_affi['name'] = affi_values[1]
    ret_art_auth_affi['short_name'] = affi_values[1]
    add_01 = ""
    if affi_values[3] != None and affi_values[3]  != "" and affi_values[3] != smallest_unit:
        add_01 = affi_values[3] 
    if affi_values[9] != None and affi_values[9] != "" and affi_values[9] != smallest_unit:
        if add_01 != "":
               add_01 += ", "+ affi_values[9]
        else:
               add_01 += affi_values[9]
    if affi_values[2] != None and affi_values[2] != "" and affi_values[2] != smallest_unit:
        if add_01 != "":
               add_01 += ", "+ affi_values[2]
        else:
               add_01 += affi_values[2]
    if add_01 != "":
        ret_art_auth_affi['add_01'] = add_01
        ret_art_auth_affi['add_02'] = addr_values[1] 
        ret_art_auth_affi['add_03'] = addr_values[2]
        ret_art_auth_affi['add_04'] = addr_values[3]
        ret_art_auth_affi['add_05'] = addr_values[4]
    else:
        ret_art_auth_affi['add_01'] = addr_values[1]
        ret_art_auth_affi['add_02'] = addr_values[2] 
        ret_art_auth_affi['add_03'] = addr_values[3]
        ret_art_auth_affi['add_04'] = addr_values[4]
        
    ret_art_auth_affi['country'] = addr_values[5]
    ret_art_auth_affi['affiliation_id'] = affi_values[0]
    ret_art_auth_affi['created_at'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    ret_art_auth_affi['updated_at'] = ret_art_auth_affi['created_at'] 
    return ret_art_auth_affi                

def build_address_row(affi, affi_vals):
    address_row = [0,None,None,None,None,None]
    if 'address' in affi_vals:
        address_row[1] = affi_vals['address']
    if 'country' in affi_vals:
        address_row[5] = affi_vals['country']
    else:
        address_row[5] = affi[5]
    return address_row

def add_author_affiliation(db_conn, art_aut_id, affi_id, affi_values):
    if affi_id in [0,None,''] or \
       affi_values['country'] in [None,''] or\
       affi_values['institution'] in [None,'']:
        return None
    print("Creating ", art_aut_id, affi_id, affi_values)
    affiliation_row = list(db_conn.get_row("affiliations", affi_id))[0]
    address_row = build_address_row(affiliation_row, affi_values)
    print("Affiliation values", affiliation_row)
    print("Address values", address_row )
    new_auth_affi = make_author_affiliation(art_aut_id, affiliation_row, address_row)
    print('Adding:', new_auth_affi)
    new_aa_id = db_conn.put_values_table("author_affiliations", new_auth_affi.keys(), new_auth_affi.values())
    return new_aa_id

def is_affi_ok(an_affi):
    affi_ok = True
    institution_ok = country_ok = sector_ok = no_blank_fields = True
    if an_affi['institution'] in ['', None]:
        institution_ok = False
    if an_affi['sector'] in ['', None]:
        sector_ok = False
    if an_affi['country'] in ['', None]:
        country_ok = False
    for field in an_affi.values():
        if field == "":
            no_blank_fields = False
            break
    if not institution_ok or not country_ok \
       or not sector_ok or not no_blank_fields:
        affi_ok = False
    return affi_ok


def add_new_affiliation(db_conn, affi_values):
    print('processing:',affi_values )
    if not is_affi_ok(affi_values):
        return 0;
    add_update_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    affiliation_new = affi_values
    del affiliation_new['address']
    if 'address' in affiliation_new.keys():
        del affiliation_new['address']
    if 'num' in affiliation_new.keys():
        del affiliation_new['num']
    affiliation_new['created_at'] = add_update_time
    affiliation_new['updated_at'] = add_update_time
    affiliation_id = db_conn.put_values_table("affiliations", affiliation_new.keys(), affiliation_new.values())
    print('processed:',affi_values )
    return affiliation_id

def update_author_affiliation(db_conn, aut_affi_id, affi_id, affi_values):
    print("Updating", aut_affi_id, affi_values)
    affiliation_row = list(db_conn.get_row("affiliations", affi_id))[0]
    address_row = [0,None,None,None,None,None]
    if 'address' in affi_values:
        address_row[1] = affi_values['address']
    if 'country' in affi_values:
        address_row[5] = affi_values['country']
    else:
        address_row[5] = affiliation_row[5]
   
    auth_affi = make_author_affiliation(0, affiliation_row, address_row)
    update_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    
    print(auth_affi)
    for affi_col in auth_affi:
        if not affi_col in ["article_author_id", "created_at"]:
            new_value = auth_affi[affi_col]
            if isinstance(new_value, str):# new_value != None and not isinstance(new_value, int):
                if "'" in new_value: new_value = new_value.replace("'","''")
                if "’" in new_value: new_value = new_value.replace("’","''")
            print("updating aut_affi_id:", aut_affi_id, "column:", affi_col, "value:", new_value)
            db_conn.set_value_table('author_affiliations', aut_affi_id,  affi_col, new_value)
            

def update_cr_aai(db_conn, cr_affi_id, auth_affi_id):
    s_table = 'cr_affiliations'
    s_field = 'author_affiliation_id'
    db_conn.set_value_table(s_table, cr_affi_id,  s_field , auth_affi_id)

def check_affiliation_consistency(current_db):
    all_ok = False
    x = '1'
    while x != '0':
        hit_counter = 0
        all_affiliations = get_all_affiliations(current_db)
        for an_affi in all_affiliations:
            if not is_affi_ok(an_affi):
                print("Inconsistent affiliation:", an_affi)
                hit_counter +=1
        if hit_counter == 0:
            
            all_ok = True
            break
        x =input()
    return all_ok


def check_for_synonyms(current_db,affi_parser):
    all_ok = False
    x = '1'
    while x != '0':
        hit_counter = 0
        all_affiliations = get_all_affiliations(current_db)
        for an_affi in all_affiliations:
            if an_affi['institution'] in affi_parser.institution_synonyms.keys():
                hit_counter += 1 
                print(hit_counter, "Institution synonym in affiliation:", an_affi['id'],
                      an_affi['institution'],
                      'it should be', affi_parser.institution_synonyms[an_affi['institution']])
        if hit_counter == 0:
            
            all_ok = True
            break
        x =input()
    return all_ok

def check_for_duplicates(current_db):
    all_ok = False
    x = '1'
    while x != '0':
        hit_counter = 0
        all_affiliations = get_all_affiliations(current_db)
        for an_affi in all_affiliations:
            for other_affi in all_affiliations:
                if an_affi['id'] != other_affi['id'] and an_affi['institution'] == other_affi['institution']:
                    found_dups = True
                    for a_key in ['department', 'work_group', 'faculty', 'school', 'country', 'sector']:
                        if an_affi[a_key] != other_affi[a_key]:
                            found_dups = False
                            break
                    if found_dups:
                        hit_counter += 1 
                        print(hit_counter, "Institution duplicates:",
                              "\n\t", an_affi['id'], an_affi['institution'],'\n\t',
                              other_affi['id'], other_affi['institution'])
                        print("update author_affiliations set affiliation_id = %s where affiliation_id = %s;"%(an_affi['id'],other_affi['id']))
                        print("delete from affiliations where id = %s;"%other_affi['id'])
                        
        if hit_counter == 0:            
            all_ok = True
            break
        x =input()
    return all_ok

def are_all_one_liners(db_conn, cr_parser, cr_affi_lines):
    all_one_liners = True
    for a_cr_line in cr_affi_lines:
        one_line_affi = is_one_line_affi(cr_parser, a_cr_line[1])
        print( a_cr_line[1], one_line_affi)
        if not one_line_affi:
            all_one_liners = False
    return all_one_liners

def check_cr_affis_vs_affiliations(current_db,affi_parser):
    all_ok = True
    x = '1'
    already_ok = open_ok_list('ok_cr_affis.txt')
    with_problems = []
    #last_checked = already_ok[-1:][0]
    #print(last_checked)
    list_art_aut_ids = get_cr_affis_article_author_ids(current_db)
    for art_aut_id in list_art_aut_ids:
        #if not art_aut_id in already_ok and art_aut_id >  last_checked:
        if art_aut_id > 0:
            print('{0:#^100}'.format(' Check article author %s '%(art_aut_id) ))
            cr_lines = get_cr_lines_for_article_author_ids(current_db, art_aut_id)
            print('{0:*^80}'.format('CR Affilitations found:'), "\n", cr_lines)
            if are_all_one_liners(current_db, affi_parser, cr_lines):
                assigned_ok = False
                print('{0:*^80}'.format('verify one liners'))
                for a_cr_line in cr_lines:                        
                    if not check_assigned_affi_ol(current_db, affi_parser, a_cr_line):
                        print("Problems with ", a_cr_line[0])
                        print('{0:*^80}'.format(" Problems with affiliation: %s for author: %s "%(cr_lines[0][3], art_aut_id)))
                        parsed_lines = affi_parser.parse_and_map_multiline(cr_lines)
                        if can_be_assigned(current_db, affi_parser, parsed_lines):
                            correct_oneline(current_db, affi_parser, cr_lines)
                        else:
                            print('{0:#^80}'.format(" cannot generate author affilitions for %s affiliations not found ")%(art_aut_id))
                            print(a_cr_line[0])
                            with_problems.append(a_cr_line[0])
                            all_ok = False
                            #input()
                            #break
                    else:
                        already_ok.append(a_cr_line[0])
            else:
                print('verify multiline affi')
                assigned_ok = check_assigned_affi_ml(current_db, affi_parser, cr_lines, art_aut_id)
                if not assigned_ok:
                    print('{0:@^80}')
                    print('{0:@^80}'.format(" Problems with: %s %s "%(cr_lines[0][2], art_aut_id)))
                    parsed_lines = affi_parser.parse_and_map_multiline(cr_lines)
                    if can_be_assigned(current_db, affi_parser, parsed_lines):
                        correct_multiline(current_db, affi_parser, cr_lines)
                    else:
                        print('{0:#^80}'.format(" cannot generate author affilitions for %s affiliations not found ")%(art_aut_id))
                        print(cr_lines)
                        crs_wiht_issues = [x[0] for x in cr_lines]
                        with_problems += crs_wiht_issues
                    #input()
                    all_ok = False
                    #break
                else:
                    crs_ok = [x[0] for x in cr_lines]
                    already_ok += crs_ok
                    print(already_ok[-20:])
            save_ok_list(already_ok, 'ok_cr_affis.txt')
            save_ok_list(with_problems, 'prob_cr_affis.txt')
    return all_ok
    
def save_ok_list(values_list, file_name):
    with open(file_name, 'w') as f:
        for an_id in values_list:
            f.write(str(an_id)+'\n')

def open_ok_list(file_name):
    with open(file_name) as f:
        lines = f.readlines()
    from_file = []
    for a_line in lines:
        from_file.append(int(a_line.replace('\n','')))
    return from_file       

if __name__ == "__main__":        
    # database name
    app_db = '../mcc_data/development.sqlite3'
    # initialise parser
    affi_parser = get_parser(app_db)
    db_connection = dbh.DataBaseAdapter(app_db)
    # Verify affiliations table:
    #   all affiliations are consistent
    #   there are no synonyms in affiliations table
    #   there are no duplicates in affiliations table
    if check_affiliation_consistency(db_connection): print ("OK, no inconsistent affiliations")

    if check_for_synonyms(db_connection,affi_parser): print ("OK, no synonyms in institutions")
    
    if check_for_duplicates(db_connection): print ("OK, no duplicate affiliations")

    check_cr_affis_vs_affiliations(db_connection, affi_parser)
    
    
