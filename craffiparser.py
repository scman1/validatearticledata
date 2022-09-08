# library for connecting to the db
from sqlite3 import dbapi2 as sqlite

class crp:
    #db_conn = dbh.DataBaseAdapter('./db_files/production.sqlite3')
    def __init__(self,dbname):
        self.con=sqlite.connect(dbname)
        
    def __del__(self):
        self.con.close( )
    
    def get_value_list(self, table, column):
        results = self.con.execute('select %s from %s group by %s' %
                                  (column, table, column)).fetchall( )
        value_list = []
        for result in results:
            for item in result:
                value_list.append(item)
        if '' in value_list: value_list.remove('')
        if None in value_list: value_list.remove(None)
        return value_list
    
    def start_lists(self):
        # get institutions list from affiliations table
        print("Refreshing lists")
        self.institutions_list = self.get_value_list("affiliations", "institution")
        # get coutries from affiliations table
        self.countries_list = self.get_value_list("affiliations","country")
        # get school list from affiliations table
        self.schools_list = self.get_value_list("Affiliations","school")
        # get department list from affiliations table
        self.departments_list = self.get_value_list("affiliations","department")
        # get faculty list from affiliations table
        self.faculties_list = self.get_value_list("affiliations","faculty")
        # get research group list from affiliations table
        self.groups_list = self.get_value_list("affiliations", "work_group")
    

        self.affi_keys = {'a':'institution', 'b':'country', 'c':'department','d':'faculty',
                     'e':'work_group', 'f':'school' }

        self.country_synonyms = {"(UK)":"United Kingdom", "UK":"United Kingdom",
                            "U.K.":"United Kingdom", "U. K.":"United Kingdom",
                            "U.K":"United Kingdom", "PRC":"Peoples Republic of China",
                            "P.R.C.":"Peoples Republic of China", 
                            "P.R.China":"Peoples Republic of China",
                            "P. R. China":"Peoples Republic of China",
                            "P.R. China":"Peoples Republic of China","China":"Peoples Republic of China",
                            "United States":"United States of America",
                            "USA":"United States of America","U.S.A.":"United States of America",
                            "U. S. A.":"United States of America", "U.S.":"United States of America",
                            "U. S.":"United States of America","US":"United States of America",
                           }

        self.institution_synonyms = {"Paul Scherrer Institut":"Paul Scherrer Institute",
                                "PSI":"Paul Scherrer Institute",
                                "Diamond Light source Ltd": "Diamond Light Source Ltd.",
                                "Diamond Light Source": "Diamond Light Source Ltd.",
                                "University of St Andrews": "University of St. Andrews",
                                "Queen’s University of Belfast":"Queen's University Belfast",
                                "STFC":"Science and Technology Facilities Council",
                                "University of Manchester": "The University of Manchester",
                                "Finden Limited": "Finden Ltd",
                                "The ISIS facility":"ISIS Neutron and Muon Source",
                                "ISIS Neutron and Muon Facility":"ISIS Neutron and Muon Source",
                                "ISIS Pulsed Neutron and Muon Facility":"ISIS Neutron and Muon Source",
                                "STFC":"Science and Technology Facilities Council",
                                "Oxford University":"University of Oxford",
                                "University of St Andrews":"University of St. Andrews",
                                "Diamond Light Source Ltd Harwell Science and Innovation Campus":"Diamond Light Source Ltd.",
                                "Diamond Light Source":"Diamond Light Source Ltd.",
                                "ISIS Facility":"ISIS Neutron and Muon Source",
                                "University College of London":"University College London",
                                "UCL":"University College London", "UOP LLC":"UOP LLC, A Honeywell Company",
                                "University of Manchester":"The University of Manchester",
                                "Johnson-Matthey Technology Centre":"Johnson Matthey Technology Centre",
                                "Research Complex at Harwell (RCaH)":"Research Complex at Harwell",
                                "RCaH":"Research Complex at Harwell",
                                "Queens University Belfast":"Queen's University Belfast",
                                "Queen’s University Belfast":"Queen's University Belfast",
                                "University of Edinburgh":"The University of Edinburgh",
                                "SynCat@Beijing, Synfuels China Technology Co. Ltd.":"SynCat@Beijing Synfuels China Company Limited",
                                "Synfuels China Compnay Limited":"SynCat@Beijing Synfuels China Company Limited",
                                "Finden Limited":"Finden Ltd",
                                "The UK Catalysis Hub":"UK Catalysis Hub",
                                "Univ. Pablo de Olavide":"Universidad Pablo de Olavide",
                                "Univ Rennes":"Université de Rennes",
                                "Université Rennes":"Université de Rennes",
                                "Institut Laue Langevin":"Institut Laue-Langevin",
                                "Esfera UAB":"Universitat Autònoma de Barcelona",
                                "Kings College London":"King's College London",
                               }  

        self.country_exceptions = ["Denmark Hill", "UK Catalysis Hub", "Sasol Technology U.K.", "N. Ireland", 'Indian']

    # Check the if any of the values in the list is in the given string
    def check_list(self, a_string, a_list):
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

    # verify if the string has some of the synomyms in the provided synonym table
    def str_has_synonym(self, affi_str, synonym_dict):
        ret_str = ""
        temp_str = ""
        for a_key in synonym_dict.keys():
            if a_key in affi_str:
                if len(a_key) > len(temp_str):
                    temp_str = a_key
        if len(temp_str) > 0:
            ret_str = synonym_dict[temp_str]
            affi_str = affi_str.replace(temp_str,'')
        return ret_str, affi_str

    def remove_extra_commas(self, str_this):
        str_this = str_this.replace(", ,", "")
        str_this = str_this.replace("; ;", "")
        str_this = str_this.replace(" ;", ";")
        str_this = str_this.replace(" ,", ",")
        str_this = str_this.strip()
        if not str_this[-1:].isalpha():
            str_this = str_this[:-1]
        if len(str_this) <= 1:
            return ""
        first_alpha = str_this.find([a_char for a_char in str_this if a_char.isalpha() ][0])
        if first_alpha != 0:
           str_this = str_this[first_alpha:]
        return str_this.strip()

    
    # try to split affiliation
    def split_single(self, affiliation_str):
        inst_str = dept_str = faculty_str = group_str = ctry_str = school_str = ""

        splitting_this = affiliation_str
        # lookup using institution synonyms table
        inst_str, splitting_this = self.str_has_synonym(splitting_this, self.institution_synonyms)
        # Lookup using list of institutions 
        if inst_str == "":
            inst_str, splitting_this = self.check_list(splitting_this, self.institutions_list)

        #  lookup using Country Synonyms table
        ctry_str, splitting_this = self.str_has_synonym(splitting_this, self.country_synonyms)
        #  lookup using Countries list        
        if ctry_str == "":
            ctry_str, splitting_this = self.check_list(splitting_this, self.countries_list)

        # Lookup using department list
        dept_str, splitting_this = self.check_list(splitting_this, self.departments_list)

        # Lookup using school list
        school_str, splitting_this = self.check_list(splitting_this, self.schools_list)

        # Lookup using faculty list
        faculty_str, splitting_this = self.check_list(splitting_this, self.faculties_list)
        
        # Lookup using group list
        group_str, splitting_this = self.check_list(splitting_this, self.groups_list)
        
        splitting_this = self.remove_extra_commas(splitting_this)

        return_parsed = {'institution':inst_str, 'school': school_str,
                         'department': dept_str, 'faculty': faculty_str,
                         'work_group': group_str, 'country': ctry_str,
                         'address':  splitting_this}
        # use this to eliminate empties
        # return_parsed = {k:v for k,v in return_parsed.items() if v != ''}
        return return_parsed

    def parse_multiline(self, affi_list):
        print("Parsing", affi_list)
        return_parsed = []
        parsed_affi = { }
        for a_line in affi_list:
            sl_elements = self.split_single(a_line)
            if parsed_affi == {}:
                parsed_affi = sl_elements
            else:
                sl_elements_no_blanks = {k:v for k,v in sl_elements.items() if v != ''}
                sl_keys = sl_elements_no_blanks
                for a_key in sl_keys:
                    if parsed_affi[a_key] == '':
                        parsed_affi[a_key] = sl_elements_no_blanks[a_key]
                    elif parsed_affi[a_key] != '' and a_key == 'address' :
                        parsed_affi[a_key] = sl_elements_no_blanks[a_key]
        return_parsed.append(parsed_affi)
        return return_parsed
           

    def get_from_string(self, string_value, element):
        element_value = ""
        print("************ get",element,"*************************")
        print("split and add this: ", string_value)
        element_value = self.extract_custom(string_value)
        string_value = string_value.replace(element_value,'')
        string_value = self.remove_extra_commas(string_value)
        return element_value, string_value

    def manual_split_address(self, affiliation_values):
        opt_end = False
        while (opt_end == False):
            print(affiliation_values)
            missing_vals = {}
            int_idx = 1
            for an_element in affiliation_values:
                if affiliation_values[an_element] == "":
                    missing_vals[int_idx] = an_element
                    int_idx += 1
            print('Which element to get from string:')
            for an_idx in missing_vals:
                print(" ", an_idx, missing_vals[an_idx])
            print (" ", len(missing_vals)+1, 'end')
            print('Selection')
            option_sel = int(input())
            if option_sel == len(missing_vals)+1:
                opt_end = True
            elif option_sel > 0 and option_sel <= len(missing_vals):
                print("Try to extract ", missing_vals[option_sel])
                affiliation_values[missing_vals[option_sel]], affiliation_values['address'] = \
                self.get_from_string(affiliation_values['address'], missing_vals[option_sel])
        return affiliation_values

    def extract_custom(self, split_this):
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

if __name__ == "__main__":
    # Testing parser for single line affiliation
    import craffiparser
    cr_parse = craffiparser.crp("../mcc_data/development.sqlite3")
    cr_parse.start_lists()
    affi_string = "Departament de Ciència de Materials i Química Física & Institut de Química Teòrica i Computacional (IQTCUB)"
    parsed_list = cr_parse.split_single(affi_string)
    print(parsed_list)
    # Test manual split
    affi_string = 'Department of Environmental Sciences, University of Basel, Bernoullistrasse 32, Basel 4056, Switzerland'
    parsed_list = cr_parse.split_single(affi_string)
    manual_parse = cr_parse.manual_split_address(parsed_list)
    print(manual_parse)
    # Test parse multiline
    # A) Simple: one affiliation in more than one line
    mla_simple = [(29, 'School of Science and Technology', 80, 3516, '2022-08-24 11:50:08.873479', '2022-08-30 14:01:35.627024'),
                  (30, 'Nottingham Trent University', 80, 3516, '2022-08-24 11:50:08.886550', '2022-08-30 14:01:35.640246'),
                  (31, 'Nottingham', 80, 3516, '2022-08-24 11:50:08.902845', '2022-08-30 14:01:35.661514'),
                  (32, 'UK', 80, 3516, '2022-08-24 11:50:08.914753', '2022-08-30 14:01:35.677513')]
    just_affi_lines = [x[1] for x in mla_simple]
    pmla_simple = cr_parse.parse_multiline(just_affi_lines)
    print(pmla_simple)
    # B) Hosted: one institution hosted by another (e.g. UKCH hosted by RCaH)
    mla_hosted = [(647, 'Cardiff Catalysis Institute', 552, 915, '2022-08-24 11:51:02.702859', '2022-08-28 21:59:50.958252'),
                  (648, 'School of Chemistry', 552, 915, '2022-08-24 11:51:02.709894', '2022-08-28 21:59:50.970522'),
                  (649, 'Cardiff University', 552, 915, '2022-08-24 11:51:02.717235', '2022-08-28 21:59:50.979549'),
                  (650, 'Cardiff', 552, 915, '2022-08-24 11:51:02.727471', '2022-08-28 21:59:50.996194'),
                  (651, 'UK', 552, 915, '2022-08-24 11:51:02.735337', '2022-08-28 21:59:51.004846')]

    # C) Additional: More than one affiliation in the set
    mla_additional =[(922, 'School of Chemistry', 710, 281, '2022-08-24 11:51:23.140779', '2022-08-28 20:34:23.889324'),
                    (923, 'Cardiff University', 710, 281, '2022-08-24 11:51:23.151003', '2022-08-28 20:34:23.902953'),
                    (924, 'Cardiff CF10 3AT', 710, 281, '2022-08-24 11:51:23.159050', '2022-08-28 20:34:23.921712'),
                    (925, 'UK', 710, 281, '2022-08-24 11:51:23.165877', '2022-08-28 20:34:23.932153'),
                    (926, 'UK Catalysis Hub', 710, 282, '2022-08-24 11:51:23.176635', '2022-08-28 20:34:23.949838')]

    # D) Redundant: Duplicate elements or elements which cannot be parsed
    #    1) element duplicated
    mla_redundant_1 = [(1834, 'School of Chemistry', 1210, 469, '2022-08-24 11:52:10.755049', '2022-08-28 21:07:58.823088'),
                       (1835, 'University of Leeds', 1210, 469, '2022-08-24 11:52:10.762317', '2022-08-28 21:07:58.833093'),
                       (1836, 'Leeds LS2 9JT', 1210, 469, '2022-08-24 11:52:10.772644', '2022-08-28 21:07:58.841728'),
                       (1837, 'UK', 1210, 469, '2022-08-24 11:52:10.780377', '2022-08-28 21:07:58.858861'),
                       (1838, 'School of Chemistry', 1210, -1, '2022-08-24 11:52:10.788217', '2022-08-24 11:52:10.788217')]

    #    2) element not found
    mla_redundant_2 = [(3268, 'Department of Materials', 2289, 652, '2022-08-24 11:54:03.060683', '2022-08-28 21:33:57.352289'),
                       (3269, 'Imperial College London', 2289, 652, '2022-08-24 11:54:03.067016', '2022-08-28 21:33:57.358940'),
                       (3270, 'London SW7 2AZ', 2289, 652, '2022-08-24 11:54:03.074129', '2022-08-28 21:33:57.375765'),
                       (3271, 'UK', 2289, 652, '2022-08-24 11:54:03.082660', '2022-08-28 21:33:57.386242'),
                       (3272, 'Department of Materials Science and Engineering', 2289, -1, '2022-08-24 11:54:03.092100', '2022-08-24 11:54:03.092100')]

