# Tests for parser and helper
# library for connecting to the db
import lib.handle_db as dbh

# datetime parsing
from datetime import datetime

import craffiparser
import craffiparserhelper as aph

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

if __name__ == "__main__":        
    # database name
    app_db = '../mcc_data/development_2024bk.sqlite3' #'../mcc_data/development.sqlite3'
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

    aph.check_cr_affis_vs_affiliations(db_connection, affi_parser)
    
    test_list = [16,17,18,73,78,79,273,276,277,473,622,623,627]
    # test_list = [1,17, 244,704,1704,5521,5526,2568,2906,2909]
    # test_list = [1,171,852,1379,1984,2523,5604,5710,5788,5907,5914,6061,6140]
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

    for an_author in test_list:
        all_one_liners = True
        print('{0:*^80}'.format(' Author %s ')%(an_author), "\n")      
        cr_affi_lines = aph.get_cr_lines_for_article_author_ids(db_connection,an_author)
        for a_cr_line in cr_affi_lines:
            one_line_affi = aph.is_one_line_affi(affi_parser, a_cr_line[1])
            print( a_cr_line[1], one_line_affi)
            if not one_line_affi:
                all_one_liners = False
        if all_one_liners:
            print('check as one liners')
            assigned_ok = False
            print('{0:*^80}'.format('verify one liners'))
            for a_cr_line in cr_affi_lines:
                assigned_ok = aph.check_assigned_affi_ol(db_connection, affi_parser, a_cr_line)
                print(assigned_ok)
                if not assigned_ok:
                    print("Problems with ", a_cr_line[0])
                    break

