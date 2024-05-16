# Tests for parser and helper
# library for connecting to the db
import lib.handle_db as dbh

# datetime parsing
from datetime import datetime

import craffiparser
import craffiparserhelper as aph

import os

## Helper functions

# print the parsed affi
def print_dict(an_affi):
        for an_id, a_key in enumerate(an_affi):
            print("\t", an_id, a_key+":", an_affi[a_key])

# print a banner or separator
def print_banner(a_str):
    print('{0:#^80}'.format(a_str))

# add timestamps to a dict
def add_timestamps(a_dict):
    a_dict['created_at'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    a_dict['updated_at'] = a_dict['created_at'] 

# test if string is empty (""or "   ") or null
def str_empty_or_null(a_str):
    return not a_str or not a_str.strip()

# remove empties from dict
def remove_dict_empties(a_dict):
    no_empties_dict = a_dict.copy()
    for a_key in a_dict:
        if a_dict[a_key] == None or str(a_dict[a_key]).strip()=="":
            no_empties_dict.pop(a_key)
    return no_empties_dict

## Functions to get/add/modify DB records

def add_values_to_db(db_conn, table_name, values_dict):
    values_dict = remove_dict_empties(values_dict)
    new_id = db_conn.put_values_table(table_name, list(values_dict.keys()), list(values_dict.values()))
    return new_id

def update_cr_affiliation(db_conn, cr_affi_id, aut_affi_id):
    db_conn.set_value_table('cr_affiliations', cr_affi_id, 'author_affiliation_id', aut_affi_id)

def update_added_in_cr_affis(db_conn, art_auth_id, aut_affi_id):
    cr_affi_lines = aph.get_cr_lines_for_article_author_ids(db_conn, art_auth_id)
    for a_cr_line in cr_affi_lines :
        cr_affi_id = a_cr_line[0]
        update_cr_affiliation(db_conn, cr_affi_id, aut_affi_id)

def get_record(db_conn,table,rec_id):
    vals = db_conn.get_row(table, rec_id)
    ti = db_conn.get_table_info(table)
    return dict(zip ([x[1] for x in ti],vals[0]))

def get_a_val(db_conn, table, field, id_field, id_value):
    ret_val = None
    try:
        a_val = db_conn.get_value(table, field, id_field, id_value)
        ret_val = a_val[0]
    except:
        print ("Val not found, will return null")
    return ret_val

##  Functions to build address from parsed CR lines

# Get Addresses from a parsed affiliation
# Get Addresses from a parsed affiliation
# need to add affi_id for each address

# get the smallest unit in parsed affi
def get_smallest(parsed_affi):
    #id Institution> Faculty > School > Department > Work_group + address + Country
    smallest_unit = ""
    if not str_empty_or_null (parsed_affi['work_group']):
        smallest_unit = "work_group"
    elif not str_empty_or_null (parsed_affi['department']): 
        smallest_unit = 'department'
    elif not str_empty_or_null (parsed_affi["school"]): 
        smallest_unit = "school"
    elif not str_empty_or_null (parsed_affi["faculty"]):
        smallest_unit = "faculty"
    return smallest_unit

def make_address_from_parsed(parsed_affi):
    add_parsed = {}
    smallest_unit_key = get_smallest(parsed_affi)
    add_part = ""
    #id Institution> Faculty > School > Department > Work_group + address + Country
    if smallest_unit_key != "faculty" and not str_empty_or_null(parsed_affi["faculty"]):
        add_part += parsed_affi["faculty"]
    if smallest_unit_key != "school" and not str_empty_or_null(parsed_affi["school"]):
        if len(add_part)> 0:
            add_part += ", " + parsed_affi["school"]
        else:
            add_part += parsed_affi["school"]
    if smallest_unit_key != "department" and not str_empty_or_null(parsed_affi["department"]):
        if len(add_part)> 0:
            add_part += ", " + parsed_affi["department"]
        else:
            add_part += parsed_affi["department"]
    
    if add_part != "":
        add_parsed['add_01'] = add_part
        add_parsed['add_02'] = parsed_affi["address"] 
    else:
        add_parsed['add_01'] = parsed_affi["address"]        
    add_parsed['country'] = parsed_affi["country"]
    add_parsed['affiliation_id'] = None
    add_timestamps(add_parsed)
    return add_parsed

def test_is_empty_or__null():
    a_str = " "
    a_str = ""
    a_str = None
    print(str_empty_or_null( a_str))

def test_make_address_from_parsed():
    a_parse = {'institution': 'Tsinghua University', 
               'school': 'School of Materials Science and Engineering', 
               'country': 'Peoples Republic of China', 
               'faculty': "Faculty of Engineering",
               "department": "Department of Chemistry",
               "work_group":"Key Laboratory of Advanced Materials",
               'address': "Beijing 100084"}

    print(make_address_from_parsed(a_parse))

    # test FSDG
    test_keys=["faculty","school","department","work_group"]
    for idx in range(0,16):
        test_affi_p = a_parse.copy()
        a_test="{:04b}".format(idx)
        if a_test[0] == '0': test_affi_p["faculty"] = ""
        if a_test[1] == '0': test_affi_p["school"] = ""
        if a_test[2] == '0': test_affi_p["department"] = ""
        if a_test[3] == '0': test_affi_p["work_group"] = ""
        print ("testing ", a_test)
        print(make_address_from_parsed(test_affi_p))
        
# run these tests if the code is changed
# test_is_empty_or__null()

# test_make_address_from_parsed()

##  Functions that create affiliation from parsed affiliation lines

def make_affiliation_from_parsed(parsed_affi):
    new_affi = parsed_affi.copy()
    new_affi.pop("address")
    sel_sector = '9'
    print_dict(new_affi)
    the_sectors = {"0":"Academia", "1":"Industry","2":"Research Facility"}
    while not sel_sector in ['0','1','2',]:
        print ("select sector for this affiliation")
        print_dict(the_sectors)
        sel_sector = input()
    new_affi["sector"]=the_sectors[sel_sector]
    
    add_timestamps(new_affi)
    
    return new_affi

def test_make_affiliation_from_parsed():
    a_parse = {'institution': 'Tsinghua University', 
               'school': 'School of Materials Science and Engineering', 
               'country': 'Peoples Republic of China', 
               'faculty': "Faculty of Engineering",
               "department": "Department of Chemistry",
               "work_group":"Key Laboratory of Advanced Materials",
               'address': "Beijing 100084"}

    # test FSDG
    test_keys=["faculty","school","department","work_group"]
    for idx in range(0,16):
        test_affi_p = a_parse.copy()
        a_test="{:04b}".format(idx)
        if a_test[0] == '0': test_affi_p["faculty"] = ""
        if a_test[1] == '0': test_affi_p["school"] = ""
        if a_test[2] == '0': test_affi_p["department"] = ""
        if a_test[3] == '0': test_affi_p["work_group"] = ""
        print ("testing ", a_test)
        print(make_affiliation_from_parsed(test_affi_p))
        
#test_make_affiliation_from_parsed()

##  Functions that create author affiliation from affiliation, address and art_author_id

def make_author_affiliation(new_affiliation, new_affi_address, art_aut_id):
    new_aut_affi = {}
    smallest_unit_key = get_smallest(new_affiliation)
    new_aut_affi["article_author_id"] = art_aut_id
    if str_empty_or_null(smallest_unit_key): new_aut_affi["name"] = new_affiliation['institution'] 
    else:  new_aut_affi["name"] = new_affiliation[smallest_unit_key]+", "+ new_affiliation['institution']
    new_aut_affi["short_name"] = new_affiliation['institution']
    if "add_01" in list(new_affi_address.keys()): new_aut_affi["add_01"] = new_affi_address["add_01"]
    if "add_02" in list(new_affi_address.keys()): new_aut_affi["add_02"] = new_affi_address["add_02"]
    if "add_03" in list(new_affi_address.keys()): new_aut_affi["add_03"] = new_affi_address["add_03"]
    if "add_04" in list(new_affi_address.keys()): new_aut_affi["add_04"] = new_affi_address["add_04"]
    if "add_05" in list(new_affi_address.keys()): new_aut_affi["add_05"] = new_affi_address["add_05"]
    new_aut_affi["affiliation_id"]=new_affiliation["id"]
    new_aut_affi["country"] =  new_affiliation['country']
    add_timestamps(new_aut_affi)
    return new_aut_affi

def test_make_author_affiliation():
    a_parse = {'institution': 'Tsinghua University', 
               'school': 'School of Materials Science and Engineering', 
               'country': 'Peoples Republic of China', 
               'faculty': "Faculty of Engineering",
               "department": "Department of Chemistry",
               "work_group":"Key Laboratory of Advanced Materials",
               'address': "Beijing 100084"}
    art_aut_id = 15
    an_affiliation = make_affiliation_from_parsed(a_parse)
    an_addres = make_address_from_parsed(a_parse)
    print(make_author_affiliation(an_affiliation, an_addres, art_aut_id))

#test_make_author_affiliation()

## Handle parsing of CR Lines

# Edit a parsed affi, in case there are errors
def fix_affi(an_affi):
    opt_edit = 0
    max_parts=len(an_affi)
    while opt_edit in range(0,max_parts):
        print("+"*80)
        print_parsed(an_affi)
        print("\t", max_parts, "end editing")
        print("+"*80)
        opt_edit = int(input())
        if opt_edit in range(0,len(an_affi)):
            the_key = list(an_affi.keys())[opt_edit] 
            print("enter value for", the_key)
            print ("current value", an_affi[the_key])
            an_affi[the_key] = input()
    return an_affi

# print the parsed affi
def print_parsed(an_affi):
        for an_id, a_key in enumerate(an_affi):
            print("\t", an_id, a_key+":", an_affi[a_key])

# print a banner or separator
def print_banner(a_str):
    print('{0:#^80}'.format(a_str))

# add affiliation and update author    
    # 1 add new affi
    # 2 add author_affi
    # 3 update the cr_entry
def add_affi_and_update_author(db_conn, art_auth_id, ok_affi):
    print_banner(f" Will save this parsed affi and assing to {art_auth_id} ")
    print_parsed(ok_affi)
    print_banner("")
    print("do it")
    # create address row from affi
    new_affi_address = make_address_from_parsed(ok_affi)
    # create affi
    new_affiliation = make_affiliation_from_parsed(ok_affi)
    # add affiliation
    new_affi_id = add_values_to_db(db_conn, "affiliations", new_affiliation)
    # create author affiliation
    new_affiliation["id"] = new_affi_id
    new_author_affiliation = make_author_affiliation(new_affiliation, new_affi_address, art_auth_id)
    # add address
    new_affi_address["affiliation_id"] = new_affi_id
    new_address_id = add_values_to_db(db_conn, "addresses", new_affi_address)
    # add author affiliation
    new_auth_affi_id = add_values_to_db(db_conn, "author_affiliations", new_author_affiliation)
    # update cr_affiliations
    update_added_in_cr_affis(db_conn, art_auth_id, new_auth_affi_id)
    return new_auth_affi_id

def assing_affi_to_author(db_conn, art_auth_id, affi_id):
    # get affiliation 
    affiliation_rec = get_record(db_conn,"affiliations",affi_id)
    # get address
    addr_id = get_a_val(db_connection,"addresses",  "id", "affiliation_id", affi_id)
    # some affiliations will have no address
    if addr_id != None:
        address_rec = get_record(db_conn,"addresses",addr_id)
    else:
        address_rec = {"country": affiliation_rec["country"]}
    # build author affiliation
    new_author_affiliation = make_author_affiliation(affiliation_rec, address_rec, art_auth_id)
    # save author affiliation
    new_auth_affi_id = add_values_to_db(db_conn, "author_affiliations", new_author_affiliation)
    # update cr_affis
    print(f"Will assign {new_auth_affi_id} to {art_auth_id}")
    update_added_in_cr_affis(db_conn, art_auth_id, new_auth_affi_id)
    return new_auth_affi_id

# edit and add
# if selected eddit and add call fix and then use the result 
# to call add_affi_and_update_author
def edit_and_add(db_conn, cr_parser, art_auth_id, new_affi):
    edited_affi = fix_affi(new_affi) 
    new_aut_affi_id = add_affi_and_update_author(db_conn, art_auth_id, edited_affi)

# try to assing parsed affi
def try_to_assign(db_conn, cr_parser, auth_id):
    cr_affi_lines = aph.get_cr_lines_for_article_author_ids(db_conn,auth_id)
    parsed_lines = affi_parser.parse_and_map_multiline(cr_affi_lines)
    for one_parsed in parsed_lines:
        print (cr_affi_lines)
        # Find an affiliation that matches the parsed lines
        affi_id = aph.get_affi_from_parsed(db_conn, one_parsed[0])
        print_parsed(one_parsed[0])
        if affi_id != None:
            print_banner(f"affilition {affi_id} found for {auth_id}")
            assign_choice=None
            while not assign_choice in ['1','2','3']:
                print(" 1 - assign found?\n 2 - edit and add new?\n 3 - do nothing\n Selection:")
                assign_choice = input()
            if assign_choice == '1':
                print(f"Assigning {affi_id} to{auth_id}")
                assing_affi_to_author(db_conn, auth_id, affi_id)
            elif sel_val =='2':
                print(f"Edit it before adding and assigning to {auth_id}")
                edit_and_add(db_conn, cr_parser, auth_id, one_parsed[0])
            else:
                print(f"Leave it for now {auth_id}")
        else:
            print_banner(f"  Affilitions for {auth_id} not found  ")
            sel_val = 0
            while not sel_val in ['1','2','3']:
                print(" 1 - add as it is?\n 2 - edit and add?\n 3 - do nothing\n Selection:")
                sel_val = input()
            if sel_val == '1':
                print(f"Adding as it is and assigning to{auth_id}")
                add_affi_and_update_author(db_conn, auth_id, one_parsed[0])
            elif sel_val == '2':
                print(f"Edit it before adding and assigning to {auth_id}")
                edit_and_add(db_conn, cr_parser, auth_id, one_parsed[0])
    
# add a new author affiliation    
def add_author_affiliation(db_conn, art_aut_id, affi_id, add_id):
    print("Arguments",art_aut_id, affi_id, add_id)
    affiliation_row = list(db_conn.get_row("affiliations", affi_id))[0]
    address_row = list(db_conn.get_row("addresses", add_id))[0]
    #print("Affiliation values", affiliation_row)
    #print("Address values", address_row )
    
    #print ("Press key to continue")
    #input()
    new_aut_affi = make_author_affiliation(art_aut_id, affiliation_row, address_row)
    #print("Parsed author affiliation:",  address_row)
    new_aa_id = db_conn.put_values_table("author_affiliations", new_aut_affi.keys(), new_aut_affi.values())
    return new_aa_id

# add a new address
def add_address(db_conn, addr_str, affi_id, ctry_str):
    add_update_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    affi_address = {'add_01':addr_str,"affiliation_id":affi_id,'country':ctry_str,
                    'created_at': add_update_time, 'updated_at':add_update_time}
    add_id = db_conn.put_values_table("addresses", affi_address.keys(), affi_address.values())
    return add_id

# add an affiliation
def add_affiliation(db_conn, affi_values):
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
    return affiliation_id

## Ceck DB is OK
# Verify affiliations tables:
#   all affiliations are consistent
#   there are no synonyms in affiliations table
#   there are no duplicates in affiliations table

def check_tables_ok (db_connection, affi_parser):
    if aph.check_affiliation_consistency(db_connection): print ("OK, no inconsistent affiliations")
    if aph.check_for_synonyms(db_connection,affi_parser): print ("OK, no synonyms in institutions")
    if aph.check_for_duplicates(db_connection): print ("OK, no duplicate affiliations")

# verify assignation of affiliations to cr_affis
def check_cr_affi_assignated(db_connection, affi_parser):
    aph.check_cr_affis_vs_affiliations(db_connection, affi_parser)

if __name__ == "__main__":        
    # database name
    clear = lambda: os.system('cls')
 
    app_db = '../mcc_data/development_2024bk.sqlite3' #'../mcc_data/development.sqlite3'
    # initialise parser
    affi_parser = aph.get_parser(app_db)
    db_connection = dbh.DataBaseAdapter(app_db)

    # verify db tables
    check_tables_ok (db_connection, affi_parser)

    # verify assigned affiliations
    check_cr_affi_assignated(db_connection, affi_parser)

    test_list = [7345, 7346, 7348, 7349, 7352, 7360, 7361, 7362,
                 7363, 7452, 7453, 7504, 7545, 7546, 7548, 7551,
                 7555, 7568, 7569, 7570, 7585, 7587, 7626, 7627,
                 7628, 7630, 7631, 7773, 7777, 7809, 7810, 7926,
                 8004, 8007, 8008, 8025, 8038, 8056, 8058, 8163,
                 8164, 8165, 8172, 8173, 8174, 8178, 8180, 8192,
                 8198, 8201, 8203, 8204, 8205, 8206, 8207, 8208,
                 8209, 8210, 8213, 8495, 8498, 8563, 8571, 8574,
                 8655, 8805, 8814, 8848, 8997, 8998, 9000, 9170,
                 9281, 9282, 9288, 9311, 9312, 9394, 9395, 9400,
                 9401, 9868, 9870, 9872, 9907]

    for art_aut_id in test_list:
        # check if affi os assigned
        cr_lines = aph.get_cr_lines_for_article_author_ids(db_connection, art_aut_id)
        can_proceed = False
        for onr_cr_line in cr_lines:
            if onr_cr_line[3] == None:
                can_proceed = True
                
        if can_proceed: 
            print ("Need to assign affiliation")
            try_to_assign(db_connection, affi_parser, art_aut_id)
        else: print(f"Affiliation for art. author {art_aut_id} parsed and assigned")
        print(f"Press any key to continue")
        input()
        clear()