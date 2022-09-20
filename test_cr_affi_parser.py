# Tests for parser and helper
# library for connecting to the db
import lib.handle_db as dbh

# datetime parsing
from datetime import datetime

import craffiparser
import craffiparserhelper as aph

def are_all_one_liners(db_conn, cr_parser, cr_affi_lines):
    all_one_liners = True
    for a_cr_line in cr_affi_lines:
        one_line_affi = aph.is_one_line_affi(cr_parser, a_cr_line[1])
        #print( a_cr_line[1], one_line_affi)
        if not one_line_affi:
            all_one_liners = False
    return all_one_liners

def check_affi_assigned_vs_cr_affi(db_conn, cr_parser,auth_id):
    cr_affi_lines = aph.get_cr_lines_for_article_author_ids(db_conn, auth_id)
    parsed_lines = affi_parser.parse_and_map_multiline(cr_affi_lines)
    if aph.can_be_assigned(db_conn, cr_parser, parsed_lines):
        print('Assigned Ok')
    else:
        print('{0:#^80}'.format(" cannot generate author affilitions for %s affiliations not found ")%(auth_id))
        print(cr_affi_lines)
        print("parsed as")
        print(parsed_lines)

def test_parse(db_conn, cr_parser,auth_id):
    cr_affi_lines = aph.get_cr_lines_for_article_author_ids(db_conn,auth_id)
    parse_result = cr_parser.parse_and_map_multiline(cr_affi_lines)
    print('{0:*^80}'.format('CR Affilitations for %s found: ')%(auth_id), "\n")
    print(cr_affi_lines)
    print('{0:*^80}'.format('Parsing Results:'), "\n")
    print(parse_result)
        
def test_correct_multiline(db_name, cr_parser, auth_id):
    cr_affi_lines = aph.get_cr_lines_for_article_author_ids(db_name,auth_id)
    correct_multiline(db_name, cr_parser, cr_affi_lines)

def test_can_be_assinged(db_name, cr_parser, auth_id):
    cr_affi_lines = aph.get_cr_lines_for_article_author_ids(db_name,auth_id)
    parsed_lines = affi_parser.parse_and_map_multiline(cr_affi_lines)
    if not aph.can_be_assigned(db_name, cr_parser, parsed_lines):
        print('{0:#^80}'.format(" cannot generate author affilitions for %s affiliations not found ")%(auth_id))
        print(cr_affi_lines)
        print("parsed as")
        print(parsed_lines)

def custom_split(db_name, cr_parser, affiliation_values, affi_string):
    # Look for institution name should be in the address element
    print ("Select how to parse ",  affiliation_values)
    option_how = 0
    while not option_how in [1,2,3,4]:
        print('options: ')
        print('1: enter data manually')
        print('2: manual parse')
        print('3: correct parse result')
        print('4: do nothing ')
        print('selection:')
        str_opt = input()
        if str_opt != '':
            option_how = int(str_opt)
    if option_how == 1:
        affiliation_values = institution_manual_entry(affiliation_values)
    elif option_how == 2:
        affiliation_values = cr_parser.manual_split_address(affiliation_values)
    elif option_how == 3:
        # get an empty affi struct and only fill in address with the affi_string
        clean_affi = {a_key:'' for a_key in affiliation_values.keys()}
        clean_affi['address'] = affi_string
        clean_affi['country'] = affiliation_values['country']
        affiliation_values = cr_parser.manual_split_address(clean_affi)
    print (affiliation_values)
    return affiliation_values

# process addresses which are a single string
def process_single_affi(db_name, cr_parser, cr_affi_id, art_aut_id, cr_affi_str):
    #clear_output()
    print('{0:*^80}')
    print("* Art. author", art_aut_id, "Affi:", cr_affi_str, "Affi ID:", cr_affi_id)
    # 1. split the single string using keywords list and synonyms tables
    affi_values = cr_parser.split_single(cr_affi_str)
    print("* Affi Values:", affi_values)
    affiliation_id = address_id = 0
    # determine if parsing needs help (institution found?)   
    if affi_values['institution'] in ["", None]:
        affi_values = custom_split(db_name, cr_parser, affi_values, cr_affi_str)
    if not affi_values['institution'] in ["", None]:
        affiliation_id = aph.get_affi_from_parsed(db_name, affi_values)
        if not affiliation_id in [0, None,'']:
            print("* Affiliation found in DB id:", affiliation_id)
            print('* Add author affiliation')
        else:
            print("* Need to add affiliation")
            print ('* Try to add affi for', affi_values)
            opt_ok_correct = 0
            while not opt_ok_correct in [1,2]:
                print("choose sector:\n\t1. Add as it is\n\t2. Correct Parsed" )
                opt_ok_correct = int(input())
                if opt_ok_correct == 2:
                    affi_values = custom_split(db_name, cr_parser, affi_values, cr_affi_str)
            address_string = affi_values['address']
            sel_sector = 0
            while not sel_sector in [1,2,3]:
                print("choose sector:\n\t1. Academia\n\t2. Industry\n\t3. Research Facility" )
                sel_sector = int(input())
                if sel_sector == 1:
                    affi_values['sector']='Academia'
                elif sel_sector == 2:
                    affi_values['sector']='Industry'
                elif sel_sector == 3:
                    affi_values['sector']='Research Facility'
            affi_no_blanks = {k:v for k,v in affi_values.items() if v != ''}
            affiliation_id = aph.add_new_affiliation(db_name, affi_no_blanks)
            # renew lists as new affi is added
            aph.refresh_lists(cr_parser)
            #address_id = add_address(address_string, affiliation_id, affi_values['country'])
            print ('* Added affiliation ', affiliation_id)#' with address ', address_id)
            
        if affiliation_id !=0 : #and address_id != 0:
            print("* Adding author affiliation record ")
            new_affi_id = aph.add_author_affiliation(db_name, art_aut_id, affiliation_id, affi_values)
            print("* Added author affiliation record ID:", new_affi_id)
            aph.update_cr_aai(db_name, cr_affi_id, new_affi_id)
            print("* Updated cr affiliation", cr_affi_id)
    else: 
        print('could not process string:', cr_affi_str)
        print('results obtained:', affi_values)
    print('{0:&^80}'.format(''))



if __name__ == "__main__":        
    # database name
    app_db = '../mcc_data/development.sqlite3'
    # initialise parser
    affi_parser = aph.get_parser(app_db)
    db_connection = dbh.DataBaseAdapter(app_db)
    # Verify affiliations table:
    #   all affiliations are consistent
    #   there are no synonyms in affiliations table
    #   there are no duplicates in affiliations table
    if aph.check_affiliation_consistency(db_connection): print ("OK, no inconsistent affiliations")

    if aph.check_for_synonyms(db_connection,affi_parser): print ("OK, no synonyms in institutions")
    
    if aph.check_for_duplicates(db_connection): print ("OK, no duplicate affiliations")

    #aph.check_cr_affis_vs_affiliations(db_connection, affi_parser)
    
    #test_list = [1,17, 244,704,1704,5521,5526,2568,2906,2909]
    test_list = [1,171,852,1379,1984,2523,5604,5710,5788,5907,5914,6061,6140]
    test_list = [1,171,]
    #test_parse(db_connection, affi_parser, test_list)
    # [244,245] two affis, second affi is only a institution name
    # 5521 two affis, one affi is hosted
    # test_correct_multiline(db_connection, affi_parser, 245)
    #test_can_be_assinged(db_connection, affi_parser, 2112)

##    for an_author in test_list:
##        if not test_can_be_assinged(db_connection, affi_parser, an_author):
##            test_parse(db_connection, affi_parser, an_author)
##        input()
##    for an_author in test_list:
##        check_affi_assigned_vs_cr_affi(db_connection, affi_parser, an_author)
##        input()

    

##    for an_author in test_list:
##        print('{0:#^100}'.format(' check as author %s '%(an_author) ))
##        cr_affi_lines = aph.get_cr_lines_for_article_author_ids(db_connection,an_author)
##        if are_all_one_liners(db_connection, affi_parser, cr_affi_lines):
##            print('{0:*^80}'.format('verify one liners'))
##            for a_cr_line in cr_affi_lines:
##                if not aph.check_assigned_affi_ol(db_connection, affi_parser, a_cr_line):
##                    print("Problems with ", a_cr_line[0])
##
##    ok_affis = aph.open_ok_list('ok_cr_affis.txt')
##    ok_affis = list(set(ok_affis))
##    print("OK Affis:%i"%(len(ok_affis)))
##    prob_affis = aph.open_ok_list('prob_cr_affis.txt')
##    
##    prob_affis = list(set(prob_affis))
##    print("Problem Affis:%i"%(len(prob_affis)))
##    a_table = 'cr_affiliations'
##    all_cr_affis = db_connection.get_full_table(a_table)
##    wrong_aa_list = []
##    new_aa_list = []
##    authors_with_issues=[]
##    for a_cr_line in all_cr_affis:
##        cr_id = int(a_cr_line[0])
##        author_id = int(a_cr_line[2])
##        if not cr_id in ok_affis and cr_id in prob_affis:
##            #print('need to add affi for:', a_cr_line)
##            new_aa_list.append(cr_id)
##            if not author_id in authors_with_issues:
##                authors_with_issues.append(author_id)
##        elif not cr_id in ok_affis and a_cr_line[3]!=None:
##            #print('wrongly assinged affi:',a_cr_line)
##            wrong_aa_list.append(cr_id)
##            if not author_id in authors_with_issues:
##                authors_with_issues.append(author_id)
##        elif not cr_id in ok_affis:
##            new_aa_list.append(cr_id)
##            if not author_id in authors_with_issues:
##                authors_with_issues.append(author_id)
##    print("Affis to add:%i"%(len(new_aa_list)))
##    for a_cr_line in all_cr_affis:
##        cr_id = int(a_cr_line[0])
##        if cr_id in new_aa_list:
##            print("New", a_cr_line)
##    print("Wrong affis :%i"%(len(wrong_aa_list)))
##    for a_cr_line in all_cr_affis:
##        cr_id = int(a_cr_line[0])
##        if cr_id in wrong_aa_list:
##            print("wrong", a_cr_line)

    authors_with_issues = [191, 192, 203, 244, 245, 281, 285, 286, 409, 411, 413, 427, 610, 701, 702, 703, 708,
                           709, 710, 711, 715, 737, 798, 841, 897, 981, 982, 991, 1066, 1078, 1101, 1102, 1159,
                           1164, 1192, 1208, 1209, 1212, 1213, 1214, 1215, 1216, 1218, 1219, 1220, 1221, 1222,
                           1324, 1336, 1379, 1432, 1599, 1600, 1607, 1644, 1666, 1672, 1673, 1676, 1678, 1681,
                           1682, 1733, 1747, 1750, 1883, 1911, 1915, 1918, 1922, 1923, 1964, 1984, 2109, 2112,
                           2114, 2115, 2117, 2183, 2188, 2232, 2233, 2235, 2318, 2319, 2328, 2329, 2332, 2349,
                           2350, 2352, 2355, 2356, 2358, 2424, 2523, 2540, 2541, 2542, 2543, 2544, 2545, 2546,
                           2552, 2553, 2556, 2568, 2576, 2604, 2607, 2644, 2645, 2650, 2654, 2655, 2685, 2704,
                           2723, 2725, 2729, 2751, 2760, 2762, 2763, 2765, 2766, 2806, 2944, 2949, 3022, 3023,
                           3024, 3025, 3216, 3218, 3288, 3289, 3292, 3293, 3294, 3304, 3305, 3306, 3308, 3309,
                           3310, 3311, 3312, 3351, 3352, 3353, 3355, 3365, 3366, 3367, 3448, 3518, 3635, 3640,
                           3658, 3799, 3800, 3801, 3805, 3806, 3917, 3957, 3958, 3964, 3968, 3981, 3982, 3983,
                           4061, 4062, 4063, 4205, 4208, 4219, 4222, 4225, 4228, 4231, 4294, 4332, 4334, 4335,
                           4336, 4337, 4350, 4369, 4370, 4372, 4381, 4387, 4389, 4391, 4422, 4537, 4583, 4586,
                           4621, 4622, 4727, 4729, 4778, 4779, 4781, 4786, 4806, 4880, 4924, 4981, 4988, 4989,
                           5012, 5046, 5088, 5093, 5094, 5182, 5183, 5197, 5290, 5292, 5293, 5294, 5295, 5296,
                           5298, 5313, 5314, 5315, 5316, 5317, 5408, 5448, 5451, 5456, 5553, 5555, 5556, 5575,
                           5585, 5586, 5589, 5594, 5600, 5602, 5604, 5611, 5613, 5620, 5623, 5640, 5641, 5642,
                           5686, 5689, 5690, 5692, 5693, 5696, 5710, 5747, 5748, 5753, 5756, 5802, 5806, 5831,
                           5834, 5866, 5869, 5870, 5902, 5907, 5908, 5914, 5936, 5937, 5959, 5981, 5995, 5996,
                           5997, 5998, 6011, 6032, 6033, 6039, 6041, 6044, 6045, 6046, 6047, 6066, 6068, 6104,
                           6107, 6108, 6140, 6260, 6272, 6288, 6373, 6375, 6378, 6379, 6380, 6412, 6416, 6417,
                           6418, 6430, 6431, 6432, 6449, 6524, 6526, 6563, 6564, 6565, 6659, 6714, 6717, 6718,
                           6798, 6805, 6806, 6807, 6808, 6809, 6810, 6811, 6814, 6815, 6842, 6852, 6855, 6857,
                           6858, 6859, 6860, 6861, 6862, 6863, 6865, 6872, 6874, 6875, 6876, 6884, 6890, 6920,
                           ]

    print("Authors to correct: %i "%(len(authors_with_issues)))
    print(authors_with_issues)

    ok_list = []
    for an_author in authors_with_issues:
        print('{0:#^100}'.format(' check as author %s '%(an_author) ))
        cr_affi_lines = aph.get_cr_lines_for_article_author_ids(db_connection,an_author)
        if are_all_one_liners(db_connection, affi_parser, cr_affi_lines):
            print('{0:*^80}'.format('verify one liners'))
            for a_cr_line in cr_affi_lines:
                if not aph.check_assigned_affi_ol(db_connection, affi_parser, a_cr_line):
                    print("Problems with ", a_cr_line[0])
                    process_single_affi(db_connection, affi_parser, a_cr_line[0], an_author, a_cr_line[1])
                else:
                    ok_list.append(an_author)
        else:
            print('multiline')
            print(cr_affi_lines)
            print(aph.correct_multiline(db_connection, affi_parser, cr_affi_lines))
            
        break
            
    
# further testing:
# issue: department not correctly parsed
# offer option to parse completly or correct results
affi_line=['Department of Materials and Environmental Chemistry, Stockholm University, Svante Arrhenius väg 16C, 106 91 Stockholm, Sweden']
# issues:
#     - Name of department is incorrect
#     - Institution is missing altogether (STFC RAL)
# offer an option to enter manually (let user choose from existing ones) and add to the lists of synonyms

affi_line=['SciML, Scientific Computing Division, Rutherford Appleton Laboratory, Harwell, UK']
