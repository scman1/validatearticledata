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
    

        self.affi_keys = {
            'a':'institution', 'b':'country', 'c':'department',
            'd':'faculty', 'e':'work_group', 'f':'school'}
################################################################################
        self.country_synonyms = {
            "(UK)":"United Kingdom", "UK":"United Kingdom",
            "U.K.":"United Kingdom", "U. K.":"United Kingdom",
            "U.K":"United Kingdom", "PRC":"Peoples Republic of China",
            "P.R.C.":"Peoples Republic of China",
            "P.R.China":"Peoples Republic of China",
            "P. R. China":"Peoples Republic of China",
            "P.R. China":"Peoples Republic of China","China":"Peoples Republic of China",
            "People’s Republic of China":"Peoples Republic of China",
            "United States":"United States of America",
            "USA":"United States of America","U.S.A.":"United States of America",
            "U. S. A.":"United States of America", "U.S.":"United States of America",
            "U. S.":"United States of America","US":"United States of America",
            "Korea":"South Korea",
            "Republic of Korea":"South Korea",}
    
################################################################################
        self.institution_synonyms = {
            'A*STAR': 'Agency for Science, Technology and Research',
            'A*STAR Agency for Science, Technology and Research': 'Agency for Science, Technology and Research',
            'AWE': 'Atomic Weapons Establishment Plc',
            'AWE Public Limited Company': 'Atomic Weapons Establishment Plc',
            'AWE plc': 'Atomic Weapons Establishment Plc',
            'Atomic Weapons Establishment (AWE) Plc': 'Atomic Weapons Establishment Plc',
            'Bio Nano Consulting': 'Bio Nano Consulting Ltd',
            'CELLS-ALBA Synchrotron Light Facility': 'ALBA Synchrotron Light Source',
            'CELLS—ALBA Synchrotron': 'ALBA Synchrotron Light Source',
            'Complutense University of Madrid': 'Universidad Complutense de Madrid',
            'DGIST': 'Daegu Gyeongbuk Institute of Science & Technology (DGIST)',
            'Daegu Gyeongbuk Institute of Science & Technology': 'Daegu Gyeongbuk Institute of Science & Technology (DGIST)',
            'Defence Science Technology Laboratory (DSTL)': 'Defence Science Technology Laboratory ',
            'Diamond Light Source': 'Diamond Light Source Ltd.',
            'Diamond Light Source Ltd Harwell Science and Innovation Campus': 'Diamond Light Source Ltd.',
            'Diamond Light source Ltd': 'Diamond Light Source Ltd.',
            'ESRF': 'European Synchrotron Radiation Facility',
            'ESRF-The European Synchrotron': 'European Synchrotron Radiation Facility',
            'East China University of Science & Technology': 'East China University of Science and Technology',
            'Ecole Polytechnique Fédérale de Lausanne': 'Ecole Polytechnique Federale de Lausanne',
            'Ecole Polytechnique Fédérale de Lausanne (EPFL)': 'Ecole Polytechnique Federale de Lausanne',
            'Elettra - Sincrotrone Trieste S.C.p.A.': 'Elettra-Sincrotrone Trieste S.C.p.A.',
            'Elettra – Sincrotrone Trieste S.C.p.A.': 'Elettra-Sincrotrone Trieste S.C.p.A.',
            'Elettra – Sincrotrone Trieste, S.S.': 'Elettra-Sincrotrone Trieste S.C.p.A.',
            'Empa Materials Science and Technology': 'Empa-Swiss Federal Laboratories for Materials Science and Technology',
            'Empa − Swiss Federal Laboratories for Materials Science and Technology': 'Empa-Swiss Federal Laboratories for Materials Science and Technology',
            'Esfera UAB': 'Universitat Autònoma de Barcelona',
            'Finden Limited': 'Finden Ltd',
            'Flemish Institute for Technological Research': 'Flemish Institute for Technological Research (VITO)',
            'Flemish Institute for Technological Research, VITO NV': 'Flemish Institute for Technological Research (VITO)',
            'Friedrich-Alexander University Erlangen-Nürnberg': 'Friedrich-Alexander-Universität Erlangen-Nürnberg',
            'Fritz Haber Institute of the Max-Planck Society': 'Fritz-Haber-Institut der Max-Planck Gesellschaft',
            'Fritz-Haber Institute of the Max-Planck Society': 'Fritz-Haber-Institut der Max-Planck Gesellschaft',
            'Glasgow University': 'University of Glasgow',
            'Harwell XPS': 'HarwellXPS',
            'Honeywell Int.': 'Honeywell International Incorporated',
            'Helmut-Schmidt-University, University of the Armed Forces': 'Helmut Schmidt University - University of the Federal Armed Forces',
            'ICREA':"Institució Catalana de Recerca i Estudis Avançats",
            'IMRE': 'Institute of Materials Research and Engineering',
            'ISIS Facility': 'ISIS Neutron and Muon Source',
            'ISIS Neutron and Muon Facility': 'ISIS Neutron and Muon Source',
            'ISIS Pulsed Neutron and Muon Facility': 'ISIS Neutron and Muon Source',
            'ISIS Pulsed Neutron and Muon Source': 'ISIS Neutron and Muon Source',
            'Imperial College, London': 'Imperial College London',
            'Imperial College': 'Imperial College London',
            'Institut Laue Langevin': 'Institut Laue-Langevin',
            'Institute of Materials Research and Engineering (IMRE)': 'Institute of Materials Research and Engineering',
            'Instituto de Ciencia de Materiales de Madrid, C.S.I.C.': 'Instituto de Ciencia de Materiales de Madrid C.S.I.C.',
            'Instituto de Ciencia de Materiales de Madrid—CSIC': 'Instituto de Ciencia de Materiales de Madrid C.S.I.C.',
            'International Iberian Nanotechnology Laboratory': 'International Iberian Nanotechnology Laboratory (INL)',
            'Johnson Matthey Technology Center': 'Johnson Matthey Technology Centre',
            'Johnson-Matthey Technology Centre': 'Johnson Matthey Technology Centre',
            'KAUST': 'King Abdullah University of Science and Technology',
            'KIT': 'Karlsruhe Institute of Technology',
            'King Abdullah University of Science and Technology (KAUST)': 'King Abdullah University of Science and Technology',
            'Kings College London': "King's College London",
            'King’s College London': "King's College London",
            'Max Planck Institute for Solid State Research': 'Max-Planck Institute for Solid State Research',
            'NSG-Pilkington': 'NSG Group',
            'NTU': 'Nanyang Technological University',
            'New York University Abu Dhabi (NYUAD)': 'New York University Abu Dhabi',
            'Norwegian University of Science and Technology (NTNU)': 'Norwegian University of Science and Technology',
            'Oxford University': 'University of Oxford',
            'PSI': 'Paul Scherrer Institute',
            'Pandit Deendayal Petroleum University': 'Pandit Deendayal Energy University',
            'Paul Scherrer Institut': 'Paul Scherrer Institute',
            'Queen Mary University London': 'Queen Mary University of London',
            'Queens University Belfast': "Queen's University Belfast",
            'Queen’s University Belfast': "Queen's University Belfast",
            'Queen’s University of Belfast': "Queen's University Belfast",
            'RCaH': 'Research Complex at Harwell',
            'Research Complex at Harwell (RCaH)': 'Research Complex at Harwell',
            'Réseau sur le Stockage Electrochimique de l’Energie (RS2E)': 'Réseau sur le Stockage Électrochimique de l’Énergie (RS2E)',
            'STFC': 'Science and Technology Facilities Council',
            'Science &amp; Technology Facilities Council': 'Science and Technology Facilities Council',
            "SciTech": "SciTech Daresbury",
            'Sorbonne Universités': 'Sorbonne Université',
            'SuperSTEM': 'SuperSTEM Laboratory',
            'SynCat@Beijing, Synfuels China Technology Co. Ltd.': 'SynCat@Beijing Synfuels China Company Limited',
            'Synfuels China Compnay Limited': 'SynCat@Beijing Synfuels China Company Limited',
            'Technical University Berlin': 'Technische Universität Berlin',
            'Technion': 'Technion - Israel Institute of Technology',
            'Technion Israel Institute of Technology': 'Technion - Israel Institute of Technology',
            'Technion-Israel Institute of Technology': 'Technion - Israel Institute of Technology',
            'The European Synchrotron': 'European Synchrotron Radiation Facility',
            'The European Synchrotron. 71': 'European Synchrotron Radiation Facility',
            'The ISIS facility': 'ISIS Neutron and Muon Source',
            'The UK Catalysis Hub': 'UK Catalysis Hub',
            'The University of Liverpool': 'University of Liverpool',
            'UCL': 'University College London',
            'UKAEA': 'UK Atomic Energy Authority',
            'UOP LLC': 'UOP LLC, A Honeywell Company',
            'Univ Rennes': 'Université de Rennes',
            'Univ. Bordeaux': 'Université de Bordeaux',
            'Univ. Lille':'Université Lille',
            'Univ Limoges':'Université de Limoges',
            'Univ. Pablo de Olavide': 'Universidad Pablo de Olavide',
            'Univ. of Manchester': 'The University of Manchester',
            'Universitat Politecnica de Catalunya': 'Universitat Politècnica de Catalunya',
            'University College of London': 'University College London',
            'University of Aston': 'Aston University',
            'University of Bern': 'Universität Bern',
            'University of Berne': 'Universität Bern',
            'University of Bologna': 'Università di Bologna',
            'University of California Davis': 'University of California, Davis',
            'University of Cardiff': 'Cardiff University',
            'University of Durham': 'Durham University',
            'University of Edinburgh': 'The University of Edinburgh',
            'University of Manchester': 'The University of Manchester',
            'University of Padova': 'Università di Padova',
            'University of Padua': 'Università di Padova',
            'University of St Andrews': 'University of St. Andrews',
            'University of Trieste': 'Università degli Studi di Trieste',
            'Università degli Studi di Padova': 'Università di Padova',
            'Université Claude Bernard – Lyon 1': 'Université Claude Bernard Lyon 1',
            'Université Rennes': 'Université de Rennes',
            'Campus UAB':'Universitat Autònoma de Barcelona',
            'Wrocław University of Technology': 'Wrocław University of Science and Technology',
        }
        
        self.hosted_institutions= { 
            "UK Catalysis Hub" : "Research Complex at Harwell",
            "HarwellXPS" : "Research Complex at Harwell",
            "Research Complex at Harwell":"Science and Technology Facilities Council",
            "ISIS Neutron and Muon Source":"Science and Technology Facilities Council",
            "Institute of Materials Research and Engineering":"Agency for Science, Technology and Research",
            "SuperSTEM Laboratory":"SciTech Daresbury",
            "SciTech Daresbury":"Science and Technology Facilities Council",}

        self.country_exceptions = [
            "Denmark Hill", "UK Catalysis Hub", "UK CRG",
            "Sasol Technology U.K.", "Sasol Technology UK",
            "N. Ireland", 'Indian', 'Northern Ireland', "Australian"]
        
        self.country_provinces  = { "England":"United Kingdom",
                                    "Scotland":"United Kingdom",
                                    "Wales":"United Kingdom",
                                    "Northern Ireland":"United Kingdom",
                                    "N. Ireland":"United Kingdom",
                                    }
        

    def is_hosted(self, inst, host):
        if inst in self.hosted_institutions.keys() and \
          self.hosted_institutions[inst] == host:
            return True
        return False

    def get_host_paths(self, affi_list):
        hostings = []
        for a_affi in affi_list:
            for b_affi in affi_list:
                if self.is_hosted(a_affi, b_affi):
                    hostings.append([a_affi,b_affi])
        # get three level hostings
        host_paths = []
        for a_hosted in hostings:
            for b_hosted in hostings:
                if a_hosted[0] == b_hosted[1]:
                    host_paths.append( [b_hosted[0], b_hosted[1], a_hosted[1]])
        return hostings + host_paths

    def get_longest_path(self, paths_list):
        longest_path = []
        for a_path in paths_list:
            if longest_path == []:
                longest_path = a_path
            elif len(longest_path)< len(a_path):
                longest_path = a_path
        return longest_path 

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
        if not str_this[-1:].isalnum():
            str_this = str_this[:-1]
        if len(str_this) <= 1:
            return ""
        first_alpha = str_this.find([a_char for a_char in str_this if a_char.isalnum() ][0])
        if first_alpha != 0:
           str_this = str_this[first_alpha:]
        return str_this.strip()

    def get_institutions_in_str(self, a_str):
        remider = an_institution = ""
        # lookup on synonyms and institutions lists
        an_institution, remider = self.str_has_synonym(a_str, self.institution_synonyms)
        if an_institution == "":
            an_institution, remider = self.check_list(a_str, self.institutions_list)
        
        if an_institution == "":
            # if nothing is found return an empty list
            return [remider]
        else:
            # if somehing is found return it and look in the rest of the list
            return [an_institution] + self.get_institutions_in_str(remider)

    def check_exceptions(self, a_str):
        has_exceptions = False
        for an_exception in self.country_exceptions:
            if an_exception in a_str:
                has_exceptions =  True
        return has_exceptions
        
    def handle_country_exception(self, cr_string):
        a_country_exception = reminder_e = ""

        a_country_exception, reminder_e = self.check_list(cr_string, self.country_exceptions)
        # parse reminder of exception
        e_country, e_parsed = self.parse_countries(reminder_e)
        # Exception found at:
        exception_at = cr_string.index(a_country_exception)
        # Reinsert exception on its original position or at the end if reminder is shorter
        if exception_at < len(e_parsed):
            reminder_e = (e_parsed[:exception_at] + a_country_exception + e_parsed[exception_at:]).strip()
        else:
            reminder_e += " " + a_country_exception 
        return e_country, reminder_e

    
    def parse_countries(self, a_str):
        reminder_c = reminder_s = a_country_name = a_country_synonym = a_country_exception = reminder_e = ""
        
        # first check for country exceptions in string 
        if self.check_exceptions(a_str):
            a_country_exception, reminder_e = self.handle_country_exception(a_str)
            
        
        # lookup on synonyms and countries lists
        # if both country and synonym are found, prefer country
        # unless the synonym is for Ireland (N. Ireland and Ireland are in the UK)
        a_country_synonym, reminder_s = self.str_has_synonym(a_str, self.country_synonyms)
         
        a_country_name, reminder_c = self.check_list(a_str, self.countries_list)
        
        a_country_province, reminder_p = self.str_has_synonym(a_str, self.country_provinces)
        
        if a_country_exception != "":
            return a_country_exception, reminder_e
        
        elif a_country_name == "" and a_country_synonym == "":
            # if nothing is found return an empty list
            return '', a_str
        elif a_country_province != "":
            # if country found return country 
            return a_country_province, reminder_p
        elif a_country_name != "":
            # if country found return country 
            return a_country_name, reminder_c
        else:
            # return the synonym string
            return a_country_synonym, reminder_s

    # parse instintutions in a string:
    # taking hostings into account
    def parse_institutions(self, affiliation_str):
        institutions_list = self.get_institutions_in_str(affiliation_str)
        host_paths = self.get_host_paths(institutions_list)
        longest_path = self.get_longest_path(host_paths)
        non_inst_items = longest_path[1:]+ list(set(institutions_list) - set(longest_path))
        non_parsed = ", ".join(non_inst_items)
        a_institution = longest_path[0]
        return a_institution, non_parsed

    def get_all_synonyms_for(self, a_dict, a_str):
        synonyms_list = []
        for k,v in a_dict.items():
            if a_str == v : synonyms_list.append(k)
        return synonyms_list
    
    def parse_institutions2(self, affiliation_str):
        institutions_in_affi = self.get_institutions_in_str(affiliation_str)
        the_inst = ""
        the_synonym = ""
        #print (institutions_in_affi )
        for an_inst in institutions_in_affi:
            inst_synonyms = self.get_all_synonyms_for(self.institution_synonyms, an_inst)
            if an_inst in affiliation_str and an_inst in self.institutions_list:
                if the_inst == "":
                    the_inst = an_inst
                elif the_inst in affiliation_str and affiliation_str.index(an_inst) < affiliation_str.index(the_inst):
                    the_inst = an_inst
                elif the_synonym in affiliation_str and  affiliation_str.index(an_inst) < affiliation_str.index(the_synonym):
                    the_inst = an_inst
                    the_synonym = ""
            else:
                for a_synon in inst_synonyms:
                    if a_synon in affiliation_str:
                        if the_inst == "":
                            the_inst = an_inst
                            the_synonym = a_synon
                        elif affiliation_str.index(a_synon) < affiliation_str.index(the_synonym):
                            the_inst = an_inst
                            the_synonym = a_synon
                
        if the_synonym != "":
            non_parsed = affiliation_str.replace(the_synonym, "")
        else:
            non_parsed = affiliation_str.replace(the_inst, "")
        return the_inst, non_parsed

    def parse_dept_school_faculty_or_group(self, affiliation_str):
        parsing=[]
        parsing.append(["department"] + list(self.check_list(affiliation_str, self.departments_list)))
        parsing.append(["school"] + list(self.check_list(affiliation_str, self.schools_list)))
        parsing.append(["work_group"] +  list(self.check_list(affiliation_str, self.groups_list)))
        parsing.append(["faculty"] +  list(self.check_list(affiliation_str, self.faculties_list)))
        longest = []
        for a_result in parsing:
            if (longest == [] or len(longest[1])<len(a_result[1])) and a_result[1] != "":
                longest = a_result
        return longest            
            

    def remove_returns(self, affi_string):
        clean_str = affi_string.replace("\r", " ")
        clean_str = clean_str.replace("\n", " ")
        clean_str = clean_str.replace("\u2005", " ")
        clean_str = clean_str.replace("\u202f", " ")
        while "  " in clean_str:
            clean_str = clean_str.replace("  ", " ")
        return clean_str
        
    # try to split affiliation
    def split_single(self, affiliation_str):
        inst_str = dept_str = faculty_str = group_str = ctry_str = school_str = ""

        splitting_this = self.remove_returns(affiliation_str)
        
        # lookup using institution and institution synonyms list
        inst_str, splitting_this = self.parse_institutions2(splitting_this)

        
        while True:
            returned = self.parse_dept_school_faculty_or_group(splitting_this)
            if returned != []:
                if returned[0] == 'department':
                    dept_str = returned[1]
                if returned[0] == 'school':
                    school_str = returned[1]
                if returned[0] == 'work_group':
                    group_str = returned[1]
                if returned[0] == 'faculty':
                    faculty_str = returned[1]
                splitting_this = returned[2]
            else:
                break

        # lookup using Country Synonyms table
        # need to remove country exceptions first
        ctry_str, splitting_this = self.parse_countries(splitting_this)
##        ctry_str, splitting_this = self.str_has_synonym(splitting_this, self.country_synonyms)
##        #  lookup using Countries list        
##        if ctry_str == "":
##            ctry_str, splitting_this = self.check_list(splitting_this, self.countries_list)

      
        splitting_this = self.remove_extra_commas(splitting_this)

        return_parsed = {'institution':inst_str, 'school': school_str,
                         'department': dept_str, 'faculty': faculty_str,
                         'work_group': group_str, 'country': ctry_str,
                         'address':  splitting_this}
        # use this to eliminate empties
        # return_parsed = {k:v for k,v in return_parsed.items() if v != ''}
        return return_parsed

    def parse_multiline(self, affi_list):
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
                        parsed_affi[a_key] += ", " + sl_elements_no_blanks[a_key]
                    elif parsed_affi[a_key] != '' and a_key == 'institution':
                        if self.is_hosted(parsed_affi[a_key], sl_elements_no_blanks[a_key]):
                            parsed_affi["address"] += ", " + sl_elements_no_blanks[a_key]
                        else:
                            return_parsed.append(parsed_affi)
                            parsed_affi = sl_elements
                    else:
                        # Anything left, add it to the address (at the front)
                        parsed_affi["address"] = sl_elements_no_blanks[a_key] + ", " + parsed_affi["address"]
                        
        return_parsed.append(parsed_affi)
        return return_parsed

    def parse_and_map_single(self, single_affi):
        sl_elements = self.split_single(single_affi[1])
        return [[sl_elements, [single_affi[0]]]]
        
    def parse_and_map_multiline(self, affi_list):
        return_parsed = []
        cr_ids =[]
        parsed_affi = { }
        for a_line in affi_list:
            sl_elements = self.split_single(a_line[1])
            #print("Parsed:", a_line[1],'as', sl_elements)
            cr_ids.append(a_line[0])
            if parsed_affi == {}:
                parsed_affi = sl_elements
            else:
                sl_elements_no_blanks = {k:v for k,v in sl_elements.items() if v != ''}
                sl_keys = sl_elements_no_blanks
                for a_key in sl_keys:
                    if parsed_affi[a_key] == '':
                        parsed_affi[a_key] = sl_elements_no_blanks[a_key]
                    elif parsed_affi[a_key] != '' and a_key == 'address' :
                        parsed_affi[a_key] += ", " + sl_elements_no_blanks[a_key]
                    elif parsed_affi[a_key] != '' and a_key == 'institution':
                        if self.is_hosted(parsed_affi[a_key], sl_elements_no_blanks[a_key]):
                            parsed_affi["address"] += ", " + sl_elements_no_blanks[a_key]
                        else:
                            cr_ids.pop()
                            return_parsed.append([parsed_affi, cr_ids])
                            cr_ids = [a_line[0]]
                            parsed_affi = sl_elements
                    else:
                        # Anything left, add it to the address (at the front)
                        parsed_affi["address"] = sl_elements_no_blanks[a_key] + ", " + parsed_affi["address"]
                #print("Built:", parsed_affi)   
        return_parsed.append([parsed_affi, cr_ids])
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
    # Testing parser methods for single line affiliation
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
    
    sla_simple3 = (156, 'UK Catalysis Hub, Research Complex at Harwell, STFC Rutherford Appleton Laboratory, Didcot, Oxfordshire OX11 0FA, United Kingdom', 207, 2221, '2022-08-24 11:50:23.518165', '2022-08-28 20:34:22.457602')
    psla_simple = cr_parse.get_institutions_in_str(sla_simple3[1])
    print ("Get institutions:", psla_simple)
    hosts_list = cr_parse.get_host_paths(psla_simple)
    print ("Hostings for institutions:", hosts_list)

    sla_issues = [ (937, 'Department of Chemistry', 713, 1281, '2022-08-24 11:51:23.831822', '2022-08-28 22:12:53.325838'),
                   (17, 'AWE Aldermaston, Reading, RG7 4PR, UK', 28, 2207, '2022-08-24 11:33:33.118858', '2022-08-24 11:33:33.118858'),
                   (155, 'School of Chemistry, Cardiff University, Main Building, Park Place, Cardiff CF10 3AT, United Kingdom', 207, 256, '2022-08-24 11:50:23.504931', '2022-08-24 11:50:23.504931'),
                   (156, 'UK Catalysis Hub, Research Complex at Harwell, STFC Rutherford Appleton Laboratory, Didcot, Oxfordshire OX11 0FA, United Kingdom', 207, 2221, '2022-08-24 11:50:23.518165', '2022-08-28 20:34:22.457602'),
                   (2230, 'Advanced Membranes and Porous Materials Center, Division of Physical Science and Engineering, King Abdullah University of Science and Technology (KAUST), 23955 Thuwal, Saudi Arabia', 1601, 2008, '2022-08-24 11:52:47.017602', '2022-08-28 23:27:14.760621'),
                   (151, 'School of Chemistry and Chemical Engineering, Queen’s University Belfast, David Keir Building, Stranmillis Road, Belfast BT9 5AG, Northern Ireland', 204, 499, '2022-08-24 11:50:23.400089', '2022-08-24 11:50:23.400089'),
                   (6433, 'Department\rof Chemistry, Technion - Israel Institute of Technology, Haifa 32000, Israel', 4492, 3420, '2022-08-24 17:22:57.698032', '2022-08-24 17:22:57.698032'),
                   (6433, 'Department\r of Chemistry, Technion - Israel Institute of Technology, Haifa 32000, Israel', 4492, 3420, '2022-08-24 17:22:57.698032', '2022-08-24 17:22:57.698032'),
                   ]
    for an_affi in sla_issues:
        parsed_issues = cr_parse.split_single(an_affi[1])
        print ("Parsed with issues:", parsed_issues)


##    
##    
##    # Test parse multiline
##    # A) One affi: one affiliation in more than one line
##    mla_one_affi = [(29, 'School of Science and Technology', 80, 3516, '2022-08-24 11:50:08.873479', '2022-08-30 14:01:35.627024'),
##                  (30, 'Nottingham Trent University', 80, 3516, '2022-08-24 11:50:08.886550', '2022-08-30 14:01:35.640246'),
##                  (31, 'Nottingham', 80, 3516, '2022-08-24 11:50:08.902845', '2022-08-30 14:01:35.661514'),
##                  (32, 'UK', 80, 3516, '2022-08-24 11:50:08.914753', '2022-08-30 14:01:35.677513')]
##    just_affi_lines = [x[1] for x in mla_one_affi]
##    pml_one_affi = cr_parse.parse_multiline(just_affi_lines)
##    pml_one_affi = cr_parse.parse_and_map_multiline(mla_one_affi)
##    print('********** MULTILINE ONE AFFI *************')
##    print(mla_one_affi)
##    print('*************** PARSED AS *****************')
##    print(pml_one_affi)
##    
    # B) Hosted: one institution hosted by another (e.g. UKCH hosted by RCaH)
##    mla_hosted = [(647, 'Cardiff Catalysis Institute', 552, 915, '2022-08-24 11:51:02.702859', '2022-08-28 21:59:50.958252'),
##                  (648, 'School of Chemistry', 552, 915, '2022-08-24 11:51:02.709894', '2022-08-28 21:59:50.970522'),
##                  (649, 'Cardiff University', 552, 915, '2022-08-24 11:51:02.717235', '2022-08-28 21:59:50.979549'),
##                  (650, 'Cardiff', 552, 915, '2022-08-24 11:51:02.727471', '2022-08-28 21:59:50.996194'),
##                  (651, 'UK', 552, 915, '2022-08-24 11:51:02.735337', '2022-08-28 21:59:51.004846')]
    mla_hosted = [(843, 'UK Catalysis Hub', 693, 1260, '2022-08-24 11:51:20.586064', '2022-08-28 22:12:51.545787'),
                  (844, 'Research Complex at Harwell', 693, 1260, '2022-08-24 11:51:20.593059', '2022-08-28 22:12:51.562326'),
                  (845, 'Rutherford Appleton Laboratory', 693, 1260, '2022-08-24 11:51:20.608376', '2022-08-28 22:12:51.579334'),
                  (846, 'Didcot OX11 0FA', 693, 1260, '2022-08-24 11:51:20.616072', '2022-08-28 22:12:51.588762'),
                  (847, 'UK', 693, 1260, '2022-08-24 11:51:20.625922', '2022-08-28 22:12:51.603265')]
    mla_hosted = [(7821, 'ISIS Facility', 5521, 151, '2022-08-24 17:27:04.753191', '2022-08-24 17:27:04.753191'),
                  (7822, 'STFC Rutherford Appleton Laboratory', 5521, 822, '2022-08-24 17:27:04.797186', '2022-08-24 17:27:04.797186'),
                  (7823, 'Oxfordshire, UK', 5521, 822, '2022-08-24 17:27:04.840656', '2022-08-24 17:27:04.840656'),
                  (7824, 'Imperial College London', 5521, 6182, '2022-08-24 17:27:04.898781', '2022-08-24 17:27:04.898781'),
                  (7825, 'London SW7 2AZ, UK', 5521, 6182, '2022-08-24 17:27:04.937359', '2022-08-24 17:27:04.937359')]
    just_affi_lines = [x[1] for x in mla_hosted]
    pmla_hosted = cr_parse.parse_multiline(just_affi_lines)
    pmla_hosted = cr_parse.parse_and_map_multiline(mla_hosted)
    print('*********** MULTILINE HOSTED **************')
    print(mla_hosted)
    print('*************** PARSED AS *****************')
    print(pmla_hosted)
##    
##    # C) Additional: More than one affiliation in the set
##    mla_additional =[(922, 'School of Chemistry', 710, 281, '2022-08-24 11:51:23.140779', '2022-08-28 20:34:23.889324'),
##                    (923, 'Cardiff University', 710, 281, '2022-08-24 11:51:23.151003', '2022-08-28 20:34:23.902953'),
##                    (924, 'Cardiff CF10 3AT', 710, 281, '2022-08-24 11:51:23.159050', '2022-08-28 20:34:23.921712'),
##                    (925, 'UK', 710, 281, '2022-08-24 11:51:23.165877', '2022-08-28 20:34:23.932153'),
##                    (926, 'UK Catalysis Hub', 710, 282, '2022-08-24 11:51:23.176635', '2022-08-28 20:34:23.949838')]
##    just_affi_lines = [x[1] for x in mla_additional]
##    pmla_additional = cr_parse.parse_multiline(just_affi_lines)
##    pmla_additional = cr_parse.parse_and_map_multiline(mla_additional)
##    print('********* MULTILINE ADDITIONAL ************')
##    print(mla_additional)
##    print('*************** PARSED AS *****************')
##    print(pmla_additional)
##
##    # D) Redundant: Duplicate elements or elements which cannot be parsed
##    #    1) element duplicated
##    mla_redundant_1 = [(1834, 'School of Chemistry', 1210, 469, '2022-08-24 11:52:10.755049', '2022-08-28 21:07:58.823088'),
##                       (1835, 'University of Leeds', 1210, 469, '2022-08-24 11:52:10.762317', '2022-08-28 21:07:58.833093'),
##                       (1836, 'Leeds LS2 9JT', 1210, 469, '2022-08-24 11:52:10.772644', '2022-08-28 21:07:58.841728'),
##                       (1837, 'UK', 1210, 469, '2022-08-24 11:52:10.780377', '2022-08-28 21:07:58.858861'),
##                       (1838, 'School of Chemistry', 1210, -1, '2022-08-24 11:52:10.788217', '2022-08-24 11:52:10.788217')]
##    just_affi_lines = [x[1] for x in mla_redundant_1]
##    pmla_redundant_1 = cr_parse.parse_multiline(just_affi_lines)
##    pmla_redundant_1 = cr_parse.parse_and_map_multiline(mla_redundant_1)
##    print('********* MULTILINE DUPLICATED ************')
##    print(mla_redundant_1)
##    print('*************** PARSED AS *****************')
##    print(pmla_redundant_1)
##    
##
##    #    2) element not found
##    mla_redundant_2 = [(3268, 'Department of Materials', 2289, 652, '2022-08-24 11:54:03.060683', '2022-08-28 21:33:57.352289'),
##                       (3269, 'Imperial College London', 2289, 652, '2022-08-24 11:54:03.067016', '2022-08-28 21:33:57.358940'),
##                       (3270, 'London SW7 2AZ', 2289, 652, '2022-08-24 11:54:03.074129', '2022-08-28 21:33:57.375765'),
##                       (3271, 'UK', 2289, 652, '2022-08-24 11:54:03.082660', '2022-08-28 21:33:57.386242'),
##                       (3272, 'Department of Materials Science and Engineering', 2289, -1, '2022-08-24 11:54:03.092100', '2022-08-24 11:54:03.092100')]
##    just_affi_lines = [x[1] for x in mla_redundant_2]
##    pmla_redundant_2 = cr_parse.parse_multiline(just_affi_lines)
##    pmla_redundant_2 = cr_parse.parse_and_map_multiline(mla_redundant_2)
##    print('********** MULTILINE NOT FOUND ************')
##    print(mla_redundant_2)
##    print('*************** PARSED AS *****************')
##    print(pmla_redundant_2)

    # E) Verify looking up for department
    mla_dept = [(936, 'Kathleen Lonsdale Materials Chemistry', 713, 1281, '2022-08-24 11:51:23.823411', '2022-08-28 22:12:53.308690'),
                (937, 'Department of Chemistry', 713, 1281, '2022-08-24 11:51:23.831822', '2022-08-28 22:12:53.325838'),
                (938, 'University College London', 713, 1281, '2022-08-24 11:51:23.841547', '2022-08-28 22:12:53.336440'),
                (939, 'London WC1H 0AJ', 713, 1281, '2022-08-24 11:51:23.849915', '2022-08-28 22:12:53.351383'),
                (940, 'UK', 713, 1281, '2022-08-24 11:51:23.859373', '2022-08-28 22:12:53.364468'),]
    just_affi_lines = [x[1] for x in mla_dept]
    pmla_dept_jal = cr_parse.parse_multiline(just_affi_lines)
    pmla_dept = cr_parse.parse_and_map_multiline(mla_dept)
    print('{0:*^80}'.format(' MULTILINE DEPARTMENT '))
    print(mla_dept)
    print('{0:*^80}'.format(' PARSED AS '))
    print(pmla_dept_jal)
    print(pmla_dept)

##    # test parse and map single_affi
##    sla_simple = (1, 'Chemistry─School of Natural and Environmental Sciences, Newcastle University, Newcastle upon Tyne, NE1 7RU, U.K.', 1, 1, '2022-08-23 08:21:07.822289', '2022-08-28 18:40:22.195960')
##    psla_simple = cr_parse.parse_and_map_single(sla_simple)
##    print('********** SINGLE LINE SIMPLE ************')
##    print(sla_simple)
##    print('*************** PARSED AS *****************')
##    print(psla_simple)
##
##
##    # test parse and map single_affi
##    sla_simple = (151, 'School of Chemistry and Chemical Engineering, Queen’s University Belfast, David Keir Building, Stranmillis Road, Belfast BT9 5AG, Northern Ireland', 204, 2220, '2022-08-24 11:50:23.400089', '2022-08-24 11:50:23.400089')
##    sla_simple2 = (152, 'Department of Chemical Engineering and Analytical Science, The University of Manchester, The Mill, Sackville Street, Manchester M13 9PL, United Kingdom', 204, 499, '2022-08-24 11:50:23.412171', '2022-08-28 21:08:01.089731')
##    sla_simple3 = (156, 'UK Catalysis Hub, Research Complex at Harwell, STFC Rutherford Appleton Laboratory, Didcot, Oxfordshire OX11 0FA, United Kingdom', 207, 2221, '2022-08-24 11:50:23.518165', '2022-08-28 20:34:22.457602')
##    psla_simple = cr_parse.parse_and_map_single(sla_simple3)
##    print('********** SINGLE LINE HOSTED *************')
##    print(sla_simple3)
##    print('*************** PARSED AS *****************')
##    print(psla_simple)

    


