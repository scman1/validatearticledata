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
        print( a_cr_line[1], one_line_affi)
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

    

    for an_author in test_list:
        print('{0:#^100}'.format(' check as author %s '%(an_author) ))
        cr_affi_lines = aph.get_cr_lines_for_article_author_ids(db_connection,an_author)
        if are_all_one_liners(db_connection, affi_parser, cr_affi_lines):
            print('{0:*^80}'.format('verify one liners'))
            for a_cr_line in cr_affi_lines:
                if not aph.check_assigned_affi_ol(db_connection, affi_parser, a_cr_line):
                    print("Problems with ", a_cr_line[0])

    ok_affis = aph.open_ok_list('ok_cr_affis.txt')
    ok_affis = list(set(ok_affis))
    print("OK Affis:%i"%(len(ok_affis)))
    prob_affis = aph.open_ok_list('prob_cr_affis.txt')
    
    prob_affis = list(set(prob_affis))
    print("Problem Affis:%i"%(len(prob_affis)))
    a_table = 'cr_affiliations'
    all_cr_affis = db_connection.get_full_table(a_table)
    wrong_aa_list = []
    new_aa_list = []
    authors_with_issues=[]
    for a_cr_line in all_cr_affis:
        cr_id = int(a_cr_line[0])
        author_id = int(a_cr_line[2])
        if not cr_id in ok_affis and cr_id in prob_affis:
            #print('need to add affi for:', a_cr_line)
            new_aa_list.append(cr_id)
            if not author_id in authors_with_issues:
                authors_with_issues.append(author_id)
        elif not cr_id in ok_affis and a_cr_line[3]!=None:
            #print('wrongly assinged affi:',a_cr_line)
            wrong_aa_list.append(cr_id)
            if not author_id in authors_with_issues:
                authors_with_issues.append(author_id)
        elif not cr_id in ok_affis:
            new_aa_list.append(cr_id)
            if not author_id in authors_with_issues:
                authors_with_issues.append(author_id)
    print("Affis to add:%i"%(len(new_aa_list)))
##    for a_cr_line in all_cr_affis:
##        cr_id = int(a_cr_line[0])
##        if cr_id in new_aa_list:
##            print("New", a_cr_line)
    print("Wrong affis :%i"%(len(wrong_aa_list)))
##    for a_cr_line in all_cr_affis:
##        cr_id = int(a_cr_line[0])
##        if cr_id in wrong_aa_list:
##            print("wrong", a_cr_line)

    print("Authors to correct: %i "%(len(authors_with_issues)))
    print(authors_with_issues)
