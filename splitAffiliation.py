def split_and_assign(input_text):
    ret_parsed = {}
    fields={'a':'ResearchGroup', 'b':'Department','c':'Faculty',
            'd':'Institution','e':'Address','f':'City','g':'Country'}
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
               ret_parsed.update(split_and_assign(part))
        elif user_opt == 'b':
            assgnr = ""
            while True:
                print('Options:\n a) ResearchGroup\n b) Department\n c) Faculty\n d) Institution\n e) Address\n f) City\n g) Country')
                assgnr = input()
                print(assgnr)
                keys = list(fields.keys())
                print(keys)
                if assgnr in keys:
                    print('assing to:', assgnr, fields[assgnr])
                    ret_parsed[fields[assgnr]]=input_text
                    break;
                
    return ret_parsed

text = 'University of Groningen; Engineering and Technology Institute Groningen (ENTEG), Department of Chemical Engineering; Nijenborgh 4 9747 AG Groningen The Netherlands'

affiliation = split_and_assign(text)
